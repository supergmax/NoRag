import os
from supabase import create_client, Client
from .base import BackendBase


class SupabaseBackend(BackendBase):
    def __init__(self):
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        self.db: Client = create_client(url, key)

    def get_chunks_index(self) -> list[dict]:
        resp = self.db.table("chunks_documents").select(
            "id, titre_section, mots_cles, documents(titre)"
        ).execute()
        result = []
        for chunk in resp.data:
            result.append({
                "id": chunk["id"],
                "titre_section": chunk["titre_section"],
                "mots_cles": chunk["mots_cles"],
                "doc_titre": chunk.get("documents", {}).get("titre", "Inconnu"),
            })
        return result

    def get_chunks_by_ids(self, ids: list[int]) -> list[dict]:
        if not ids:
            return []
        resp = self.db.table("chunks_documents").select(
            "titre_section, contenu_complet"
        ).in_("id", ids).execute()
        return resp.data

    def get_memory(self, session_id: str, limit: int = 4) -> list[dict]:
        resp = (
            self.db.table("memoire_norag")
            .select("role, contenu, cree_le")
            .eq("session_id", session_id)
            .order("cree_le", desc=True)
            .limit(limit)
            .execute()
        )
        return list(reversed(resp.data))

    def save_memory(self, session_id: str, role: str, content: str) -> None:
        self.db.table("memoire_norag").insert({
            "session_id": session_id,
            "role": role,
            "contenu": content,
        }).execute()

    def add_document(self, titre: str, resume: str) -> int:
        resp = self.db.table("documents").insert({
            "titre": titre,
            "resume_global": resume,
        }).execute()
        return resp.data[0]["id"]

    def add_chunk(self, doc_id: int, titre: str, mots_cles: str, contenu: str) -> None:
        self.db.table("chunks_documents").insert({
            "document_id": doc_id,
            "titre_section": titre,
            "mots_cles": mots_cles,
            "contenu_complet": contenu,
        }).execute()

    def list_documents(self) -> list[dict]:
        resp = self.db.table("documents").select("id, titre, resume_global").execute()
        return resp.data
