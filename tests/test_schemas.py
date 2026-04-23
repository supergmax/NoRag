import pytest
from pydantic import ValidationError
from api.schemas import QueryRequest, RouterOutput, PlannerOutput, LayerPlan, DocumentRef

def test_query_request_defaults():
    q = QueryRequest(question="hi")
    assert q.mode is None
    assert q.preset is None

def test_query_request_validates_mode():
    with pytest.raises(ValidationError):
        QueryRequest(question="hi", mode="bogus")

def test_router_output_parse():
    r = RouterOutput(
        agent_id="default",
        documents=[{"doc_id": "d1", "sections": ["s1"]}],
        reasoning="x",
    )
    assert r.documents[0].doc_id == "d1"

def test_planner_output_parse():
    p = PlannerOutput(
        preset_used="A",
        reasoning="x",
        layers=[LayerPlan(agent_id="default", question="q", index_scope="all")],
    )
    assert p.layers[0].agent_id == "default"

def test_document_ref_defaults():
    d = DocumentRef(doc_id="my_doc")
    assert d.sections == []
