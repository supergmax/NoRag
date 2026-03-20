import sqlite3
import os
from .base import BackendBase

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "local", "norag.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    resume_global TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER REFERENCES documents(id),
    titre_section TEXT NOT NULL,
    mots_cles TEXT NOT NULL,
    contenu_complet TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memoire_norag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    contenu TEXT NOT NULL,
    cree_le TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class SQLiteBackend(BackendBase):
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or os.getenv("SQLITE_DB_PATH", DEFAULT_DB_PATH)
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def get_chunks_index(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.titre_section, c.mots_cles, d.titre AS doc_titre
                FROM chunks_documents c
                LEFT JOIN documents d ON c.document_id = d.id
                """
            ).fetchall()
        return [dict(r) for r in rows]

    def get_chunks_by_ids(self, ids: list[int]) -> list[dict]:
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT titre_section, contenu_complet FROM chunks_documents WHERE id IN ({placeholders})",
                ids,
            ).fetchall()
        return [dict(r) for r in rows]

    def get_memory(self, session_id: str, limit: int = 4) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT role, contenu FROM (
                    SELECT role, contenu, cree_le
                    FROM memoire_norag
                    WHERE session_id = ?
                    ORDER BY cree_le DESC
                    LIMIT ?
                ) ORDER BY cree_le ASC
                """,
                (session_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def save_memory(self, session_id: str, role: str, content: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO memoire_norag (session_id, role, contenu) VALUES (?, ?, ?)",
                (session_id, role, content),
            )

    def add_document(self, titre: str, resume: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO documents (titre, resume_global) VALUES (?, ?)",
                (titre, resume),
            )
            return cur.lastrowid

    def add_chunk(self, doc_id: int, titre: str, mots_cles: str, contenu: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO chunks_documents (document_id, titre_section, mots_cles, contenu_complet) VALUES (?, ?, ?, ?)",
                (doc_id, titre, mots_cles, contenu),
            )

    def list_documents(self) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, titre, resume_global FROM documents").fetchall()
        return [dict(r) for r in rows]
