from fastapi import APIRouter
from pydantic import BaseModel
from .. import gemini

router = APIRouter()


class ArchiveRequest(BaseModel):
    texte_brut: str


class ArchiveResponse(BaseModel):
    markdown: str


@router.post("/archive", response_model=ArchiveResponse)
async def archive(req: ArchiveRequest):
    """Envoie un texte brut à Gemini archiviste et retourne la fiche Markdown structurée."""
    markdown = gemini.archive(req.texte_brut)
    return ArchiveResponse(markdown=markdown)
