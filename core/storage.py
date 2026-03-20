"""
NoRag Core — Storage.

Abstraction de stockage pour les 3 index :
- FilesystemStorage : lecture/écriture directe de fichiers .md
- SQLiteStorage : étend le backend SQLite avec agents et résumés
- SupabaseStorage : idem pour Supabase

Chaque backend implémente la même interface pour lire/écrire les index
et gérer l'historique des sessions.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from .config import Config


class StorageBase(ABC):
    """Interface commune pour tous les backends de stockage."""

    @abstractmethod
    def load_index(self, index_name: str) -> str:
        """Charge le contenu d'un fichier index (agents/documents/history)."""

    @abstractmethod
    def save_index(self, index_name: str, content: str) -> None:
        """Sauvegarde le contenu d'un fichier index."""

    @abstractmethod
    def save_session_summary(
        self, session_id: str, summary: str, documents: list[str], exchange_count: int
    ) -> None:
        """Sauvegarde le résumé d'une session."""

    @abstractmethod
    def get_session_summaries(self, limit: int = 50) -> list[dict]:
        """Retourne les résumés des sessions (les plus récents en premier)."""

    @abstractmethod
    def save_agent(self, name: str, description: str, system_prompt: str,
                   competences: str, commands: str) -> None:
        """Sauvegarde un agent/skill."""

    @abstractmethod
    def get_agents(self) -> list[dict]:
        """Retourne la liste de tous les agents."""


class FilesystemStorage(StorageBase):
    """Stockage basé sur le système de fichiers (fichiers .md)."""

    def __init__(self, config: Config):
        self.config = config
        self._index_paths = config.get_index_paths()

    def load_index(self, index_name: str) -> str:
        path = self._index_paths.get(index_name)
        if path and path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def save_index(self, index_name: str, content: str) -> None:
        path = self._index_paths.get(index_name)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def save_session_summary(
        self, session_id: str, summary: str, documents: list[str], exchange_count: int
    ) -> None:
        # En mode filesystem, on append directement au fichier index_history.md
        from .index_builder import IndexBuilder, SessionSummary
        from datetime import datetime

        builder = IndexBuilder(self.config.data_dir)
        session = SessionSummary(
            session_id=session_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=summary,
            documents_consulted=documents,
            exchange_count=exchange_count,
        )
        builder.append_session_to_history(
            self.config.index_history_path, session
        )

    def get_session_summaries(self, limit: int = 50) -> list[dict]:
        # Parse le fichier index_history.md
        content = self.load_index("history")
        if not content:
            return []

        sessions = []
        current: dict | None = None

        for line in content.splitlines():
            if line.startswith("## 🗓️ Session:"):
                if current:
                    sessions.append(current)
                # Parse: "## 🗓️ Session: user_1 (2026-03-20)"
                parts = line.replace("## 🗓️ Session: ", "").strip()
                sid = parts.split(" (")[0] if " (" in parts else parts
                date = parts.split("(")[1].rstrip(")") if "(" in parts else ""
                current = {"session_id": sid, "date": date, "summary": "", "documents": [], "exchanges": 0}
            elif current and line.startswith("- **Résumé**"):
                current["summary"] = line.split(":", 1)[1].strip() if ":" in line else ""
            elif current and line.startswith("- **Documents consultés**"):
                docs_str = line.split(":", 1)[1].strip() if ":" in line else ""
                current["documents"] = [d.strip() for d in docs_str.split(",") if d.strip()]
            elif current and line.startswith("- **Nb échanges**"):
                try:
                    current["exchanges"] = int(line.split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    pass

        if current:
            sessions.append(current)

        return sessions[:limit]

    def save_agent(self, name: str, description: str, system_prompt: str,
                   competences: str, commands: str) -> None:
        # En mode filesystem, stocker dans data/agents/<name>.md
        agent_dir = self.config.agents_dir
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_file = agent_dir / f"{name.lower().replace(' ', '_')}.md"
        content = f"""# Agent : {name}

- **Description** : {description}
- **Compétences** : {competences}
- **Commandes** : {commands}

## System Prompt

```text
{system_prompt}
```
"""
        agent_file.write_text(content, encoding="utf-8")

    def get_agents(self) -> list[dict]:
        agents = []
        agent_dir = self.config.agents_dir
        if not agent_dir.exists():
            return agents

        for f in sorted(agent_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            name = f.stem.replace("_", " ").title()
            description = ""
            competences = ""
            commands = ""

            for line in content.splitlines():
                if line.startswith("- **Description**"):
                    description = line.split(":", 1)[1].strip() if ":" in line else ""
                elif line.startswith("- **Compétences**"):
                    competences = line.split(":", 1)[1].strip() if ":" in line else ""
                elif line.startswith("- **Commandes**"):
                    commands = line.split(":", 1)[1].strip() if ":" in line else ""

            agents.append({
                "name": name,
                "description": description,
                "competences": competences,
                "commands": commands,
                "file": str(f.relative_to(self.config.data_dir)),
            })

        return agents


class SQLiteStorage(StorageBase):
    """Stockage SQLite étendu avec agents et résumés de sessions."""

    EXTRA_SCHEMA = """
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE,
        description TEXT,
        system_prompt TEXT NOT NULL,
        competences TEXT,
        commandes TEXT,
        actif BOOLEAN DEFAULT 1,
        cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS sessions_resume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        resume TEXT NOT NULL,
        documents_consultes TEXT,
        nb_echanges INTEGER DEFAULT 0,
        derniere_activite TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS index_cache (
        name TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    def __init__(self, config: Config):
        import sqlite3
        import os

        self.config = config
        self.db_path = str(config.sqlite_db_path)
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)

        with self._conn() as conn:
            conn.executescript(self.EXTRA_SCHEMA)

    def _conn(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def load_index(self, index_name: str) -> str:
        # D'abord essayer le cache DB, sinon le filesystem
        with self._conn() as conn:
            row = conn.execute(
                "SELECT content FROM index_cache WHERE name = ?", (index_name,)
            ).fetchone()
            if row:
                return row["content"]

        # Fallback filesystem
        fs = FilesystemStorage(self.config)
        return fs.load_index(index_name)

    def save_index(self, index_name: str, content: str) -> None:
        # Sauvegarder dans le cache DB ET le filesystem
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO index_cache (name, content, updated_at)
                   VALUES (?, ?, CURRENT_TIMESTAMP)""",
                (index_name, content),
            )

        # Aussi sauvegarder le fichier .md
        fs = FilesystemStorage(self.config)
        fs.save_index(index_name, content)

    def save_session_summary(
        self, session_id: str, summary: str, documents: list[str], exchange_count: int
    ) -> None:
        docs_str = ", ".join(documents)
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO sessions_resume
                   (session_id, resume, documents_consultes, nb_echanges, derniere_activite)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (session_id, summary, docs_str, exchange_count),
            )

    def get_session_summaries(self, limit: int = 50) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT session_id, resume, documents_consultes, nb_echanges, derniere_activite
                   FROM sessions_resume ORDER BY derniere_activite DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [
            {
                "session_id": r["session_id"],
                "date": r["derniere_activite"][:10] if r["derniere_activite"] else "",
                "summary": r["resume"],
                "documents": [d.strip() for d in (r["documents_consultes"] or "").split(",") if d.strip()],
                "exchanges": r["nb_echanges"],
            }
            for r in rows
        ]

    def save_agent(self, name: str, description: str, system_prompt: str,
                   competences: str, commands: str) -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO agents
                   (nom, description, system_prompt, competences, commandes)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, description, system_prompt, competences, commands),
            )

    def get_agents(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT nom, description, competences, commandes FROM agents WHERE actif = 1"
            ).fetchall()
        return [
            {
                "name": r["nom"],
                "description": r["description"] or "",
                "competences": r["competences"] or "",
                "commands": r["commandes"] or "",
            }
            for r in rows
        ]


def get_storage(config: Config | None = None) -> StorageBase:
    """Factory : retourne le bon backend de stockage selon la configuration."""
    if config is None:
        from .config import get_config
        config = get_config()

    if config.backend == "sqlite":
        return SQLiteStorage(config)
    elif config.backend == "supabase":
        # TODO: implémenter SupabaseStorage si nécessaire
        raise NotImplementedError("SupabaseStorage pas encore implémenté dans le core")
    else:
        return FilesystemStorage(config)
