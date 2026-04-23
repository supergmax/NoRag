"""Pydantic request/response schemas for NoRag L1 and Multi_L pipelines."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


Mode = Literal["L1", "MultiL"]
Preset = Literal["A", "B", "C", "D"]


class QueryRequest(BaseModel):
    question: str
    mode: Optional[Mode] = None
    preset: Optional[Preset] = None
    max_layers: Optional[int] = None
    agent_hint: Optional[str] = None
    index_scope: Optional[str] = None


class DocumentRef(BaseModel):
    doc_id: str
    sections: list[str] = Field(default_factory=list)


class RouterOutput(BaseModel):
    agent_id: str
    documents: list[DocumentRef] = Field(default_factory=list)
    reasoning: str = ""


class LayerPlan(BaseModel):
    agent_id: str
    question: str
    index_scope: str = "all"


class PlannerOutput(BaseModel):
    preset_used: Preset
    reasoning: str = ""
    layers: list[LayerPlan]


class L1Result(BaseModel):
    mode: Literal["L1"] = "L1"
    agent_id: str
    documents_used: list[DocumentRef]
    answer: str
    tokens: dict[str, int]
    latency_ms: int


class LayerResult(BaseModel):
    agent_id: str
    answer: str
    documents_used: list[DocumentRef]


class MultiLResult(BaseModel):
    mode: Literal["MultiL"] = "MultiL"
    preset_used: Preset
    layers: list[LayerResult]
    aggregated_answer: str
    tokens: dict[str, int]
    latency_ms: int
