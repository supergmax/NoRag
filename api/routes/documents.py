from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..backend.base import BackendBase

router = APIRouter()


class ChunkIn(BaseModel):
    titre_section: str
    mots_cles: str
    contenu_complet: str


class DocumentIn(BaseModel):
    titre: str
    resume_global: str
    chunks: list[ChunkIn] = []


class DocumentOut(BaseModel):
    id: int
    titre: str
    resume_global: str


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(backend: BackendBase = Depends()):
    return backend.list_documents()


@router.post("/documents", response_model=DocumentOut, status_code=201)
async def add_document(doc: DocumentIn, backend: BackendBase = Depends()):
    doc_id = backend.add_document(doc.titre, doc.resume_global)
    for chunk in doc.chunks:
        backend.add_chunk(doc_id, chunk.titre_section, chunk.mots_cles, chunk.contenu_complet)
    return {"id": doc_id, "titre": doc.titre, "resume_global": doc.resume_global}
