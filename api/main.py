import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI

# Charger .env depuis la racine du projet NoRag
load_dotenv(Path(__file__).parent.parent / ".env")

from .backend.base import BackendBase
from .backend.sqlite_backend import SQLiteBackend
from .backend.supabase_backend import SupabaseBackend
from .routes import query, documents, archive, index

app = FastAPI(
    title="NoRag API",
    description="Système NoRag — Q&R documentaire par routage LLM",
    version="2.0.0",
)

# --- Sélection du backend ---
def get_backend() -> BackendBase:
    backend_type = os.getenv("NORAG_BACKEND", "sqlite").lower()
    if backend_type == "supabase":
        return SupabaseBackend()
    return SQLiteBackend()

# Injection du backend dans les routes via override de dépendance
app.dependency_overrides[BackendBase] = get_backend

# --- Routes ---
app.include_router(query.router, tags=["Recherche"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(archive.router, tags=["Archivage"])
app.include_router(index.router)


@app.get("/health", tags=["Système"])
def health():
    backend_type = os.getenv("NORAG_BACKEND", "sqlite")
    return {"status": "ok", "backend": backend_type}
