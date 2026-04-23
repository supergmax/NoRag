"""L1 engine: Router (SLM) + Answer (LLM) = 2 calls."""

import time
from dataclasses import dataclass, field

from api.schemas import RouterOutput, L1Result
from core.config import Config
from core.llm_client import LLMClient
from core.storage import Storage


@dataclass
class L1Engine:
    config: Config
    storage: Storage
    llm: LLMClient = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMClient(api_key=self.config.gemini_api_key)

    def _load_prompt(self, name: str) -> str:
        return (self.config.prompts_dir / name).read_text(encoding="utf-8")

    async def run(self, question: str,
                  agent_forced: str | None = None,
                  index_scope: str | None = None) -> L1Result:
        t0 = time.monotonic()

        router_prompt = self._load_prompt("router.md")
        index_md = self.storage.read_index()
        agents_md = self.storage.read_system_prompts()

        router_user = (
            f"# index.md\n{index_md}\n\n"
            f"# index_system_prompt.md\n{agents_md}\n\n"
            f"# question\n{question}\n"
        )
        if index_scope:
            router_user += f"\n# index_scope_hint\n{index_scope}\n"

        parsed, router_resp = await self.llm.generate_json(
            model=self.config.router_model,
            system=router_prompt,
            user=router_user,
        )
        try:
            route = RouterOutput.model_validate(parsed)
        except Exception:
            route = RouterOutput(agent_id="default", documents=[], reasoning="fallback")

        if agent_forced:
            route.agent_id = agent_forced

        agent_prompt = (
            self.storage.extract_agent_prompt(route.agent_id)
            or self.storage.extract_agent_prompt("default")
            or "You are a helpful documentary assistant. Cite [doc_id, section]."
        )

        doc_parts: list[str] = []
        for d in route.documents:
            text = self.storage.read_document_sections(d.doc_id, d.sections)
            if text:
                doc_parts.append(f"# {d.doc_id}\n{text}")
        doc_context = "\n\n".join(doc_parts) or "(no documents selected)"

        answer_user = f"# Documents\n{doc_context}\n\n# Question\n{question}\n"

        answer_resp = await self.llm.generate(
            model=self.config.answer_model,
            system=agent_prompt,
            user=answer_user,
        )

        latency_ms = int((time.monotonic() - t0) * 1000)
        return L1Result(
            agent_id=route.agent_id,
            documents_used=route.documents,
            answer=answer_resp.text,
            tokens={"router": router_resp.tokens, "answer": answer_resp.tokens},
            latency_ms=latency_ms,
        )
