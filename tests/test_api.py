import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.main import create_app
from api.schemas import L1Result, MultiLResult, DocumentRef, LayerResult

@pytest.fixture
def app(tmp_project, monkeypatch):
    (tmp_project / "data" / "index.md").write_text("## doc1\n", encoding="utf-8")
    (tmp_project / "data" / "index_system_prompt.md").write_text(
        "## default\n**System prompt** :\n> x\n", encoding="utf-8"
    )
    (tmp_project / "core" / "prompts" / "router.md").write_text("router", encoding="utf-8")
    (tmp_project / "core" / "prompts" / "planner.md").write_text("planner", encoding="utf-8")
    (tmp_project / "core" / "prompts" / "aggregator.md").write_text("aggregator", encoding="utf-8")
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    return create_app(project_root=tmp_project)

def test_query_defaults_to_l1(app):
    fake = L1Result(agent_id="default", documents_used=[], answer="ok",
                    tokens={"router": 1, "answer": 1}, latency_ms=1)
    with patch("api.main.L1Engine.run", new=AsyncMock(return_value=fake)):
        client = TestClient(app)
        r = client.post("/query", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json()["mode"] == "L1"

def test_query_multil_override(app):
    fake = MultiLResult(
        preset_used="A", layers=[], aggregated_answer="agg",
        tokens={"planner": 1, "layers_total": 1, "aggregator": 1}, latency_ms=1,
    )
    with patch("api.main.MultiLEngine.run", new=AsyncMock(return_value=fake)):
        client = TestClient(app)
        r = client.post("/query", json={"question": "hi", "mode": "MultiL"})
    assert r.status_code == 200
    assert r.json()["mode"] == "MultiL"

def test_query_invalid_mode(app):
    client = TestClient(app)
    r = client.post("/query", json={"question": "hi", "mode": "bogus"})
    assert r.status_code == 422

def test_documents_list(app, tmp_project):
    (tmp_project / "data" / "documents" / "acme.md").write_text("## s1\ntext", encoding="utf-8")
    client = TestClient(app)
    r = client.get("/documents")
    assert r.status_code == 200
    assert "acme" in r.json()["documents"]
