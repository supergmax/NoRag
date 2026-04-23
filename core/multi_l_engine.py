"""Multi_L engine: Planner (SLM) + N parallel L1 + Aggregator (LLM)."""

import asyncio
import time
from dataclasses import dataclass, field

from api.schemas import (
    PlannerOutput, LayerPlan, LayerResult, MultiLResult, L1Result,
)
from core.config import Config
from core.l1_engine import L1Engine
from core.llm_client import LLMClient
from core.storage import Storage


@dataclass
class MultiLEngine:
    config: Config
    storage: Storage
    llm: LLMClient = field(default=None)
    l1: L1Engine = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMClient(api_key=self.config.gemini_api_key)
        if self.l1 is None:
            self.l1 = L1Engine(config=self.config, storage=self.storage, llm=self.llm)

    def _load_prompt(self, name: str) -> str:
        return (self.config.prompts_dir / name).read_text(encoding="utf-8")

    async def run(self, question: str,
                  preset: str | None = None,
                  max_layers: int | None = None) -> MultiLResult:
        t0 = time.monotonic()
        max_layers = max_layers or self.config.multil_max_layers

        planner_prompt = self._load_prompt("planner.md")
        index_md = self.storage.read_index()
        agents_md = self.storage.read_system_prompts()

        planner_user = (
            f"# index.md\n{index_md}\n\n"
            f"# index_system_prompt.md\n{agents_md}\n\n"
            f"# question\n{question}\n\n"
            f"# preset_hint\n{preset or 'D'}\n\n"
            f"# max_layers\n{max_layers}\n"
        )
        parsed, planner_resp = await self.llm.generate_json(
            model=self.config.router_model,
            system=planner_prompt,
            user=planner_user,
        )
        try:
            plan = PlannerOutput.model_validate(parsed)
        except Exception:
            plan = PlannerOutput(
                preset_used="D", reasoning="fallback",
                layers=[LayerPlan(agent_id="default", question=question, index_scope="all")],
            )

        plan.layers = plan.layers[:max_layers]

        async def run_layer(layer: LayerPlan) -> L1Result | None:
            try:
                return await asyncio.wait_for(
                    self.l1.run(
                        question=layer.question,
                        agent_forced=layer.agent_id,
                        index_scope=None if layer.index_scope == "all" else layer.index_scope,
                    ),
                    timeout=self.config.multil_layer_timeout_s,
                )
            except Exception:
                return None

        raw_results = await asyncio.gather(*(run_layer(l) for l in plan.layers))
        successful = [r for r in raw_results if r is not None]

        if not successful:
            successful = [L1Result(
                agent_id="default", documents_used=[], answer="(all layers failed)",
                tokens={"router": 0, "answer": 0}, latency_ms=0,
            )]

        layer_results = [
            LayerResult(agent_id=r.agent_id, answer=r.answer, documents_used=r.documents_used)
            for r in successful
        ]
        layers_tokens_total = sum(
            r.tokens.get("router", 0) + r.tokens.get("answer", 0) for r in successful
        )

        aggregator_prompt = self._load_prompt("aggregator.md")
        aggregator_user = self._format_for_aggregator(question, plan.preset_used, layer_results)

        agg_resp = await self.llm.generate(
            model=self.config.aggregator_model,
            system=aggregator_prompt,
            user=aggregator_user,
        )

        latency_ms = int((time.monotonic() - t0) * 1000)
        return MultiLResult(
            preset_used=plan.preset_used,
            layers=layer_results,
            aggregated_answer=agg_resp.text,
            tokens={
                "planner": planner_resp.tokens,
                "layers_total": layers_tokens_total,
                "aggregator": agg_resp.tokens,
            },
            latency_ms=latency_ms,
        )

    def _format_for_aggregator(self, question: str, preset: str,
                                layers: list[LayerResult]) -> str:
        blocks = [f"# Question\n{question}\n", f"# preset_used\n{preset}\n"]
        for i, l in enumerate(layers, 1):
            docs = ", ".join(
                f"[{d.doc_id}, {'/'.join(d.sections)}]" for d in l.documents_used
            )
            blocks.append(f"## Layer {i} — agent={l.agent_id}\nDocs: {docs}\n\n{l.answer}")
        return "\n\n".join(blocks)
