from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from ..backend.base import BackendBase
from .. import gemini

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    session_id: str = Field(default="default")


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    session_id: str


def build_index_virtuel(chunks: list[dict]) -> str:
    lines = ["INDEX DE LA BASE DE DONNÉES :"]
    for c in chunks:
        lines.append(
            f"- ID: {c['id']} | Doc: {c.get('doc_titre', '?')} | Section: {c['titre_section']} | Mots-clés: {c['mots_cles']}"
        )
    return "\n".join(lines)


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, backend: BackendBase = Depends()):
    # 1. Mémoire
    memory_rows = backend.get_memory(req.session_id)
    memory_str = "\n".join(f"- {r['role']}: {r['contenu']}" for r in memory_rows)

    # 2. Index virtuel
    chunks_index = backend.get_chunks_index()
    index_virtuel = build_index_virtuel(chunks_index)

    # 3. Routage
    chunk_ids = gemini.router(index_virtuel, req.question)

    # 4. Extraction
    chunks = backend.get_chunks_by_ids(chunk_ids)
    context = "\n".join(
        f"\n--- Section: {c['titre_section']} ---\n{c['contenu_complet']}" for c in chunks
    ) if chunks else "Aucun document pertinent trouvé."

    # 5. Génération
    answer = gemini.generate(memory_str, context, req.question)

    # 6. Sauvegarde mémoire
    backend.save_memory(req.session_id, "user", req.question)
    backend.save_memory(req.session_id, "assistant", answer)

    sources = [c["titre_section"] for c in chunks]
    return QueryResponse(answer=answer, sources=sources, session_id=req.session_id)
