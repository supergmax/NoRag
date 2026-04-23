import pytest
from unittest.mock import AsyncMock, patch
from core.config import Config
from core.storage import Storage
from core.indexer import Indexer
from core.llm_client import LLMResponse

@pytest.mark.asyncio
async def test_ingest_appends_card_and_writes_document(tmp_project):
    cfg = Config(project_root=tmp_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    cfg.index_path.write_text("# NoRag Document Index\n", encoding="utf-8")

    idx = Indexer(config=cfg, storage=storage)

    fake = LLMResponse(
        text=(
            "## new_doc\n"
            "- **Titre** : Nouveau doc\n"
            "- **Résumé** : court résumé\n"
            "- **Sections** :\n"
            "  - `s1` — Intro — mots-clés : k1\n"
            "---DOCUMENT---\n"
            "## s1\nContenu brut\n"
        ),
        tokens=123,
    )
    with patch.object(idx.llm, "generate", new=AsyncMock(return_value=fake)):
        result = await idx.ingest(doc_id="new_doc", raw_text="texte brut du doc")

    assert result["doc_id"] == "new_doc"
    assert result["tokens"] == 123
    assert "new_doc" in cfg.index_path.read_text(encoding="utf-8")
    assert (cfg.documents_dir / "new_doc.md").exists()
    assert "Contenu brut" in (cfg.documents_dir / "new_doc.md").read_text(encoding="utf-8")

@pytest.mark.asyncio
async def test_ingest_raises_on_missing_separator(tmp_project):
    cfg = Config(project_root=tmp_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    cfg.index_path.write_text("# index\n", encoding="utf-8")
    idx = Indexer(config=cfg, storage=storage)

    bad_response = LLMResponse(text="no separator here", tokens=5)
    with patch.object(idx.llm, "generate", new=AsyncMock(return_value=bad_response)):
        with pytest.raises(ValueError, match="---DOCUMENT---"):
            await idx.ingest(doc_id="x", raw_text="raw")
