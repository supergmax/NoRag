"""
NoRag Core — Configuration centralisée.

Charge les paramètres depuis .env et/ou les variables d'environnement.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration NoRag."""

    # Racine du projet NoRag
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Répertoire de données (PDFs, index)
    data_dir: Path = field(default=None)

    # Répertoire des agents/skills
    agents_dir: Path = field(default=None)

    # Backend : "filesystem", "sqlite", "supabase"
    backend: str = "filesystem"

    # Chemins des 3 fichiers index
    index_agents_path: Path = field(default=None)
    index_documents_path: Path = field(default=None)
    index_history_path: Path = field(default=None)

    # SQLite
    sqlite_db_path: Path = field(default=None)

    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # LLM
    gemini_api_key: str = ""

    # Limites
    max_history_sessions: int = 50
    max_documents_per_route: int = 3
    history_messages_per_session: int = 4

    def __post_init__(self):
        """Charge les valeurs depuis .env et normalise les chemins."""
        load_dotenv(self.project_root / ".env")

        # Data dir
        if self.data_dir is None:
            self.data_dir = self.project_root / "data"

        # Agents dir
        if self.agents_dir is None:
            self.agents_dir = self.data_dir / "agents"

        # Index paths
        if self.index_agents_path is None:
            self.index_agents_path = self.data_dir / "index_agents.md"
        if self.index_documents_path is None:
            self.index_documents_path = self.data_dir / "index_documents.md"
        if self.index_history_path is None:
            self.index_history_path = self.data_dir / "index_history.md"

        # Backend
        self.backend = os.getenv("NORAG_BACKEND", self.backend).lower()

        # SQLite
        if self.sqlite_db_path is None:
            self.sqlite_db_path = Path(
                os.getenv("SQLITE_DB_PATH", str(self.project_root / "local" / "norag.db"))
            )

        # Supabase
        self.supabase_url = os.getenv("SUPABASE_URL", self.supabase_url)
        self.supabase_key = os.getenv("SUPABASE_KEY", self.supabase_key)

        # LLM
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)

        # Créer les répertoires si nécessaire
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)

    def get_index_paths(self) -> dict[str, Path]:
        """Retourne les 3 chemins d'index sous forme de dictionnaire."""
        return {
            "agents": self.index_agents_path,
            "documents": self.index_documents_path,
            "history": self.index_history_path,
        }


# Singleton global
_config: Config | None = None


def get_config(**kwargs) -> Config:
    """Retourne la configuration globale (crée une instance si nécessaire)."""
    global _config
    if _config is None:
        _config = Config(**kwargs)
    return _config
