"""
NoRag API — Routes pour les 3 index.

Endpoints pour lire, rebuilder et résumer les index.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path

router = APIRouter(prefix="/index", tags=["Index"])

# Répertoire data/ relatif au projet
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_DATA_DIR = _PROJECT_ROOT / "data"


class IndexResponse(BaseModel):
    name: str
    content: str
    lines: int


class RebuildResponse(BaseModel):
    agents: int
    documents: int
    history_sessions: int
    message: str


@router.get("/agents", response_model=IndexResponse)
async def get_agents_index():
    """Retourne le contenu de index_agents.md."""
    path = _DATA_DIR / "index_agents.md"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    return IndexResponse(name="agents", content=content, lines=len(content.splitlines()))


@router.get("/documents", response_model=IndexResponse)
async def get_documents_index():
    """Retourne le contenu de index_documents.md."""
    path = _DATA_DIR / "index_documents.md"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    return IndexResponse(name="documents", content=content, lines=len(content.splitlines()))


@router.get("/history", response_model=IndexResponse)
async def get_history_index():
    """Retourne le contenu de index_history.md."""
    path = _DATA_DIR / "index_history.md"
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    return IndexResponse(name="history", content=content, lines=len(content.splitlines()))


@router.get("/all", response_model=list[IndexResponse])
async def get_all_indexes():
    """Retourne les 3 index en une seule requête."""
    indexes = []
    for name in ["index_agents.md", "index_documents.md", "index_history.md"]:
        path = _DATA_DIR / name
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        indexes.append(IndexResponse(
            name=name.replace("index_", "").replace(".md", ""),
            content=content,
            lines=len(content.splitlines()),
        ))
    return indexes


@router.post("/rebuild", response_model=RebuildResponse)
async def rebuild_indexes():
    """Régénère les 3 fichiers index depuis les données."""
    from core.config import get_config
    from core.storage import get_storage

    config = get_config(project_root=_PROJECT_ROOT)
    storage = get_storage(config)

    # Compter les éléments dans chaque index
    agents = storage.get_agents()
    sessions = storage.get_session_summaries()

    # Lire le nombre de documents depuis l'index
    docs_content = storage.load_index("documents")
    doc_count = sum(1 for line in docs_content.splitlines() if line.startswith("## 📄"))

    return RebuildResponse(
        agents=len(agents),
        documents=doc_count,
        history_sessions=len(sessions),
        message=f"Index rechargés : {len(agents)} agents, {doc_count} documents, {len(sessions)} sessions",
    )
