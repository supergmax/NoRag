import pytest
from unittest.mock import AsyncMock, patch
from core.config import Config
from core.storage import Storage
from core.multi_l_engine import MultiLEngine
from core.llm_client import LLMResponse
from api.schemas import L1Result, DocumentRef

@pytest.fixture
def seeded(tmp_project):
    (tmp_project / "data" / "index.md").write_text("## doc1\n", encoding="utf-8")
    (tmp_project / "data" / "index_system_prompt.md").write_text(
        "## default\n**System prompt** :\n> x\n## juriste_conformite\n**System prompt** :\n> y\n",
        encoding="utf-8",
    )
    (tmp_project / "core" / "prompts" / "planner.md").write_text(
        "You are the planner.", encoding="utf-8"
    )
    (tmp_project / "core" / "prompts" / "aggregator.md").write_text(
        "You are the aggregator.", encoding="utf-8"
    )
    (tmp_project / "core" / "prompts" / "router.md").write_text(
        "You are the router.", encoding="utf-8"
    )
    return tmp_project

@pytest.fixture
def fake_l1_result():
    return L1Result(
        agent_id="default",
        documents_used=[DocumentRef(doc_id="doc1", sections=["s1"])],
        answer="layer answer [doc1, s1]",
        tokens={"router": 50, "answer": 100},
        latency_ms=10,
    )

@pytest.mark.asyncio
async def test_multi_l_runs_two_layers(seeded, fake_l1_result):
    cfg = Config(project_root=seeded)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = MultiLEngine(config=cfg, storage=storage)

    planner_return = (
        {
            "preset_used": "A",
            "reasoning": "perspectives",
            "layers": [
                {"agent_id": "default", "question": "q", "index_scope": "all"},
                {"agent_id": "juriste_conformite", "question": "q", "index_scope": "all"},
            ],
        },
        LLMResponse(text="{}", tokens=200),
    )
    aggregator_return = LLMResponse(text="# Synthèse\nfinal [doc1, s1]", tokens=500)

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=planner_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=aggregator_return)), \
         patch.object(engine.l1, "run",
                      new=AsyncMock(return_value=fake_l1_result)):
        result = await engine.run(question="q")

    assert result.preset_used == "A"
    assert len(result.layers) == 2
    assert "final" in result.aggregated_answer
    assert result.tokens["planner"] == 200
    assert result.tokens["aggregator"] == 500
    assert result.tokens["layers_total"] == (50 + 100) * 2

@pytest.mark.asyncio
async def test_multi_l_caps_layers_at_max(seeded, fake_l1_result, monkeypatch):
    monkeypatch.setenv("MULTIL_MAX_LAYERS", "2")
    cfg = Config(project_root=seeded)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = MultiLEngine(config=cfg, storage=storage)

    planner_return = (
        {"preset_used": "A", "reasoning": "x",
         "layers": [
             {"agent_id": "default", "question": "q", "index_scope": "all"},
             {"agent_id": "juriste_conformite", "question": "q", "index_scope": "all"},
             {"agent_id": "default", "question": "q", "index_scope": "all"},
         ]},
        LLMResponse(text="{}", tokens=10),
    )

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=planner_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=LLMResponse(text="agg", tokens=1))), \
         patch.object(engine.l1, "run",
                      new=AsyncMock(return_value=fake_l1_result)) as l1_mock:
        await engine.run(question="q")

    assert l1_mock.call_count == 2

@pytest.mark.asyncio
async def test_multi_l_fallback_on_planner_failure(seeded, fake_l1_result):
    cfg = Config(project_root=seeded)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = MultiLEngine(config=cfg, storage=storage)

    bad_planner = ({"bad": "response"}, LLMResponse(text="{}", tokens=5))

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=bad_planner)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=LLMResponse(text="agg", tokens=1))), \
         patch.object(engine.l1, "run",
                      new=AsyncMock(return_value=fake_l1_result)):
        result = await engine.run(question="q")

    assert result.preset_used == "D"
    assert len(result.layers) == 1
