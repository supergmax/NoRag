"""Read-only access to index files and raw document sections.

Documents live in `data/documents/<doc_id>.md` using `## <section_id>` headers.
"""

import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Storage:
    data_dir: Path
    documents_dir: Path

    def read_index(self) -> str:
        p = self.data_dir / "index.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def read_system_prompts(self) -> str:
        p = self.data_dir / "index_system_prompt.md"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def read_document_sections(self, doc_id: str, sections: list[str]) -> str:
        p = self.documents_dir / f"{doc_id}.md"
        if not p.exists():
            return ""
        text = p.read_text(encoding="utf-8")
        if not sections:
            return text

        parts: list[str] = []
        for section_id in sections:
            pattern = rf"^##\s+{re.escape(section_id)}\s*$(.*?)(?=^##\s+|\Z)"
            m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
            if m:
                parts.append(f"## {section_id}{m.group(1).rstrip()}")
        return "\n\n".join(parts)

    def extract_agent_prompt(self, agent_id: str) -> str | None:
        text = self.read_system_prompts()
        pattern = rf"^##\s+{re.escape(agent_id)}\s*$(.*?)(?=^##\s+|\Z)"
        m = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
        if not m:
            return None
        block = m.group(1)
        sp_match = re.search(r"\*\*System prompt\*\*\s*:?\s*\n(.*)", block, flags=re.DOTALL)
        if not sp_match:
            return None
        lines = sp_match.group(1).strip().splitlines()
        prompt_lines = [l.lstrip("> ").rstrip() for l in lines if l.strip()]
        return "\n".join(prompt_lines).strip() or None
