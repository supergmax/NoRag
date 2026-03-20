from abc import ABC, abstractmethod


class BackendBase(ABC):
    """Interface commune pour les backends SQLite et Supabase (NoRag)."""

    @abstractmethod
    def get_chunks_index(self) -> list[dict]:
        """Retourne la liste des chunks avec id, titre_section, mots_cles et le titre du document parent."""

    @abstractmethod
    def get_chunks_by_ids(self, ids: list[int]) -> list[dict]:
        """Retourne le contenu complet des chunks dont l'id est dans la liste."""

    @abstractmethod
    def get_memory(self, session_id: str, limit: int = 4) -> list[dict]:
        """Retourne les N derniers messages de la session, ordre chronologique."""

    @abstractmethod
    def save_memory(self, session_id: str, role: str, content: str) -> None:
        """Sauvegarde un message dans l'historique de la session."""

    @abstractmethod
    def add_document(self, titre: str, resume: str) -> int:
        """Insère un document et retourne son id."""

    @abstractmethod
    def add_chunk(self, doc_id: int, titre: str, mots_cles: str, contenu: str) -> None:
        """Insère un chunk associé à un document."""

    @abstractmethod
    def list_documents(self) -> list[dict]:
        """Retourne la liste de tous les documents (id, titre, resume_global)."""
