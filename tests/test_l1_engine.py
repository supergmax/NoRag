import pytest
from unittest.mock import AsyncMock, patch
from pathlib import Path
from core.config import Config
from core.storage import Storage
from core.l1_engine import L1Engine
from core.llm_client import LLMResponse

@pytest.fixture
def seeded_project(tmp_project):
    (tmp_project / "data" / "index.md").write_text(
        "## doc1\n- **Sections**: `s1`\n", encoding="utf-8"
    )
    (tmp_project / "data" / "index_system_prompt.md").write_text(
        "## default\n**System prompt** :\n> Be helpful.\n", encoding="utf-8"
    )
    (tmp_project / "data" / "documents" / "doc1.md").write_text(
        "## s1\nRelevant content here.\n", encoding="utf-8"
    )
    (tmp_project / "core" / "prompts" / "router.md").write_text(
        "You are the router.", encoding="utf-8"
    )
    return tmp_project

@pytest.mark.asyncio
async def test_l1_runs_two_calls(seeded_project, monkeypatch):
    cfg = Config(project_root=seeded_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = L1Engine(config=cfg, storage=storage)

    router_return = (
        {"agent_id": "default",
         "documents": [{"doc_id": "doc1", "sections": ["s1"]}],
         "reasoning": "only option"},
        LLMResponse(text="{}", tokens=100),
    )
    answer_return = LLMResponse(text="The answer [doc1, s1].", tokens=300)

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=router_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=answer_return)):
        result = await engine.run(question="What is s1?")

    assert result.agent_id == "default"
    assert result.documents_used[0].doc_id == "doc1"
    assert "The answer" in result.answer
    assert result.tokens["router"] == 100
    assert result.tokens["answer"] == 300

@pytest.mark.asyncio
async def test_l1_respects_agent_forced(seeded_project):
    cfg = Config(project_root=seeded_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = L1Engine(config=cfg, storage=storage)

    router_return = (
        {"agent_id": "default",
         "documents": [{"doc_id": "doc1", "sections": ["s1"]}],
         "reasoning": "x"},
        LLMResponse(text="{}", tokens=50),
    )
    answer_return = LLMResponse(text="ok [doc1, s1]", tokens=80)

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=router_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=answer_return)):
        result = await engine.run(question="q", agent_forced="default")
    assert result.agent_id == "default"

@pytest.mark.asyncio
async def test_l1_fallback_on_bad_router_json(seeded_project):
    cfg = Config(project_root=seeded_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = L1Engine(config=cfg, storage=storage)

    router_return = (
        {"bad": "json"},  # missing agent_id, documents
        LLMResponse(text="{}", tokens=10),
    )
    answer_return = LLMResponse(text="fallback answer", tokens=50)

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=router_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=answer_return)):
        result = await engine.run(question="q")
    assert result.agent_id == "default"
