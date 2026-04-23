# NoRag Backend Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the NoRag backend into two explicit pipelines — L1 (2-call minimal) and Multi_L (parallel N×L1 + aggregation) — with SLM/LLM tiering, single Gemini provider, cleaned-up filetree.

**Architecture:** One `LLMClient` abstraction over Gemini. Two engines (`l1_engine`, `multi_l_engine`) built on shared `indexer`/`storage`. FastAPI exposes `/query` with `mode` selection. Agents catalogued in `data/index_system_prompt.md` and discovered by the Router LLM itself (no duplicated config).

**Tech Stack:** Python 3.11+, FastAPI, Pydantic v2, google-genai SDK, pytest, python-dotenv, asyncio.

**Spec:** `docs/superpowers/specs/2026-04-23-norag-l1-multil-microsite-design.md`

---

## File Structure

**Delete:**
- `pres_simple_Norag.html`, `pres_simple_NoRag.pptx`, `pres_simple_Norag.pdf`
- `pres_complet_NoRag.pptx`, `pres_full_Norag.html`
- `PRESENTATION_COMMERCIALE.md`, `PRESENTATION_EXECUTIVE.md`
- `NoRag_Archiviste.md`
- `data/index_agents.md`, `data/index_history.md`
- `api/local_query.py`, `api/gemini.py`
- `api/backend/` (directory), `api/routes/` (directory)
- `core/index_builder.py`

**Rename:**
- `data/index_documents.md` → `data/index.md`

**Create:**
- `core/llm_client.py` — async wrapper around google-genai, tiered model routing
- `core/l1_engine.py` — Router + Answer pipeline
- `core/multi_l_engine.py` — Planner + N×L1 + Aggregator
- `core/prompts/router.md` — Router system prompt
- `core/prompts/planner.md` — Planner system prompt
- `core/prompts/aggregator.md` — Aggregator system prompt
- `data/index_system_prompt.md` — agent catalog
- `data/documents/` — directory for raw document text
- `api/schemas.py` — Pydantic request/response models
- `tests/` — directory
- `tests/conftest.py`
- `tests/test_llm_client.py`
- `tests/test_l1_engine.py`
- `tests/test_multi_l_engine.py`
- `tests/test_indexer.py`
- `tests/test_api.py`

**Rewrite:**
- `core/config.py` — remove 3-index paths, add model tiering + `DEFAULT_MODE`
- `core/indexer.py` — fold `index_builder` logic in; simpler ingestion to `index.md`
- `core/storage.py` — read sections from `data/documents/` (no SQLite/Supabase in phase 1)
- `api/main.py` — single-file FastAPI with `/query`, `/index/rebuild`, `/documents`
- `norag/plugins/claude.md`, `gpt.md`, `gemini.md`, `grok.md` — update to L1 flow
- `README.md` — L1/Multi_L + RAG-vs-NoRag argument
- `.env.example` — tiered models + `DEFAULT_MODE`
- `requirements.txt` — drop supabase, add pytest, pytest-asyncio, httpx

---

## Task 1: Cleanup — delete obsolete files

**Files:**
- Delete listed files/dirs

- [ ] **Step 1: Delete presentation artifacts and obsolete docs**

```bash
rm "pres_simple_Norag.html" "pres_simple_NoRag.pptx" "pres_simple_Norag.pdf"
rm "pres_complet_NoRag.pptx" "pres_full_Norag.html"
rm "PRESENTATION_COMMERCIALE.md" "PRESENTATION_EXECUTIVE.md"
rm "NoRag_Archiviste.md"
```

- [ ] **Step 2: Delete obsolete index files**

```bash
rm "data/index_agents.md" "data/index_history.md"
```

- [ ] **Step 3: Delete obsolete API entrypoints and backend subtrees**

```bash
rm "api/local_query.py" "api/gemini.py"
rm -rf "api/backend" "api/routes"
rm "core/index_builder.py"
```

- [ ] **Step 4: Rename documents index to canonical name**

```bash
git mv "data/index_documents.md" "data/index.md"
```

- [ ] **Step 5: Verify repo state**

Run: `git status`
Expected: deletions + rename staged, nothing unexpected.

- [ ] **Step 6: Commit cleanup**

```bash
git add -A
git commit -m "chore: delete obsolete presentation + 3-index legacy files"
```

---

## Task 2: Update dependencies and env template

**Files:**
- Modify: `requirements.txt`
- Modify: `.env.example`

- [ ] **Step 1: Rewrite `requirements.txt`**

```
fastapi
uvicorn[standard]
google-genai
python-dotenv
pydantic>=2.0
pypdf
pytest
pytest-asyncio
httpx
```

- [ ] **Step 2: Rewrite `.env.example`**

```
# ===== LLM providers =====
GEMINI_API_KEY=your-gemini-api-key

# ===== Model tiering =====
# Router + Planner = SLM (cheap, fast, classification)
ROUTER_MODEL=gemini-2.5-flash-lite
# Answer = strong LLM (reasoning over documents)
ANSWER_MODEL=gemini-2.5-pro
# Aggregator = strong LLM (multi-layer synthesis)
AGGREGATOR_MODEL=gemini-2.5-pro

# ===== Pipeline defaults =====
# Default mode when request omits "mode": L1 | MultiL
DEFAULT_MODE=L1
# Max parallel layers in Multi_L
MULTIL_MAX_LAYERS=3
# Timeout per layer (seconds)
MULTIL_LAYER_TIMEOUT_S=30
```

- [ ] **Step 3: Install deps locally**

Run: `pip install -r requirements.txt`
Expected: clean install, no errors.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt .env.example
git commit -m "chore: update deps + env template for tiered models"
```

---

## Task 3: Rewrite `core/config.py`

**Files:**
- Modify: `core/config.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Create `tests/conftest.py`**

```python
import os
from pathlib import Path
import pytest

@pytest.fixture
def tmp_project(tmp_path, monkeypatch):
    """Isolated project root for tests."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "documents").mkdir()
    (tmp_path / "core" / "prompts").mkdir(parents=True)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    return tmp_path
```

- [ ] **Step 2: Write failing test `tests/test_config.py`**

```python
from core.config import Config

def test_config_defaults(tmp_project, monkeypatch):
    monkeypatch.delenv("DEFAULT_MODE", raising=False)
    cfg = Config(project_root=tmp_project)
    assert cfg.default_mode == "L1"
    assert cfg.router_model == "gemini-2.5-flash-lite"
    assert cfg.answer_model == "gemini-2.5-pro"
    assert cfg.aggregator_model == "gemini-2.5-pro"
    assert cfg.multil_max_layers == 3
    assert cfg.multil_layer_timeout_s == 30
    assert cfg.index_path == tmp_project / "data" / "index.md"
    assert cfg.system_prompt_path == tmp_project / "data" / "index_system_prompt.md"
    assert cfg.documents_dir == tmp_project / "data" / "documents"
    assert cfg.prompts_dir == tmp_project / "core" / "prompts"

def test_config_env_overrides(tmp_project, monkeypatch):
    monkeypatch.setenv("DEFAULT_MODE", "MultiL")
    monkeypatch.setenv("ROUTER_MODEL", "custom-slm")
    monkeypatch.setenv("MULTIL_MAX_LAYERS", "5")
    cfg = Config(project_root=tmp_project)
    assert cfg.default_mode == "MultiL"
    assert cfg.router_model == "custom-slm"
    assert cfg.multil_max_layers == 5
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL (old Config has different fields).

- [ ] **Step 4: Rewrite `core/config.py`**

```python
"""NoRag configuration. Loads .env and exposes typed settings."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Config:
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Paths
    data_dir: Path = field(default=None)
    documents_dir: Path = field(default=None)
    prompts_dir: Path = field(default=None)
    index_path: Path = field(default=None)
    system_prompt_path: Path = field(default=None)

    # LLM
    gemini_api_key: str = ""
    router_model: str = "gemini-2.5-flash-lite"
    answer_model: str = "gemini-2.5-pro"
    aggregator_model: str = "gemini-2.5-pro"

    # Pipeline
    default_mode: str = "L1"
    multil_max_layers: int = 3
    multil_layer_timeout_s: int = 30

    def __post_init__(self):
        load_dotenv(self.project_root / ".env")

        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.documents_dir is None:
            self.documents_dir = self.data_dir / "documents"
        if self.prompts_dir is None:
            self.prompts_dir = self.project_root / "core" / "prompts"
        if self.index_path is None:
            self.index_path = self.data_dir / "index.md"
        if self.system_prompt_path is None:
            self.system_prompt_path = self.data_dir / "index_system_prompt.md"

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.router_model = os.getenv("ROUTER_MODEL", self.router_model)
        self.answer_model = os.getenv("ANSWER_MODEL", self.answer_model)
        self.aggregator_model = os.getenv("AGGREGATOR_MODEL", self.aggregator_model)

        self.default_mode = os.getenv("DEFAULT_MODE", self.default_mode)
        self.multil_max_layers = int(os.getenv("MULTIL_MAX_LAYERS", self.multil_max_layers))
        self.multil_layer_timeout_s = int(os.getenv("MULTIL_LAYER_TIMEOUT_S", self.multil_layer_timeout_s))

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)


_config: Config | None = None


def get_config(**kwargs) -> Config:
    global _config
    if _config is None or kwargs:
        _config = Config(**kwargs)
    return _config
```

- [ ] **Step 5: Run test**

Run: `pytest tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add core/config.py tests/conftest.py tests/test_config.py
git commit -m "refactor(config): tiered models + single-index paths"
```

---

## Task 4: `core/llm_client.py` — Gemini async wrapper

**Files:**
- Create: `core/llm_client.py`
- Create: `tests/test_llm_client.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import AsyncMock, patch
from core.llm_client import LLMClient, LLMResponse

@pytest.mark.asyncio
async def test_generate_returns_text_and_tokens():
    client = LLMClient(api_key="test-key")

    fake_response = type("R", (), {
        "text": "hello",
        "usage_metadata": type("U", (), {"total_token_count": 42})(),
    })()

    with patch.object(client, "_raw_generate", new=AsyncMock(return_value=fake_response)):
        resp = await client.generate(model="gemini-2.5-flash-lite",
                                     system="sys",
                                     user="hi")
    assert isinstance(resp, LLMResponse)
    assert resp.text == "hello"
    assert resp.tokens == 42

@pytest.mark.asyncio
async def test_generate_json_parses_output():
    client = LLMClient(api_key="test-key")
    fake_response = type("R", (), {
        "text": '{"agent_id": "foo", "documents": []}',
        "usage_metadata": type("U", (), {"total_token_count": 10})(),
    })()
    with patch.object(client, "_raw_generate", new=AsyncMock(return_value=fake_response)):
        parsed, raw = await client.generate_json(model="gemini-2.5-flash-lite",
                                                 system="sys", user="hi")
    assert parsed == {"agent_id": "foo", "documents": []}
    assert raw.tokens == 10
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_llm_client.py -v`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `core/llm_client.py`**

```python
"""Async wrapper around google-genai with JSON-mode helper."""

import json
import re
from dataclasses import dataclass
from google import genai
from google.genai import types


@dataclass
class LLMResponse:
    text: str
    tokens: int


class LLMClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=api_key)

    async def _raw_generate(self, model: str, system: str, user: str,
                            response_mime_type: str | None = None):
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type=response_mime_type,
        )
        return await self._client.aio.models.generate_content(
            model=model, contents=user, config=config
        )

    async def generate(self, model: str, system: str, user: str) -> LLMResponse:
        resp = await self._raw_generate(model, system, user)
        return LLMResponse(
            text=resp.text or "",
            tokens=getattr(resp.usage_metadata, "total_token_count", 0),
        )

    async def generate_json(self, model: str, system: str, user: str) -> tuple[dict, LLMResponse]:
        resp = await self._raw_generate(model, system, user,
                                        response_mime_type="application/json")
        text = resp.text or ""
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON found in response: {text[:200]}")
            parsed = json.loads(match.group(0))
        return parsed, LLMResponse(
            text=text,
            tokens=getattr(resp.usage_metadata, "total_token_count", 0),
        )
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_llm_client.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/llm_client.py tests/test_llm_client.py
git commit -m "feat(core): LLMClient async wrapper with JSON mode"
```

---

## Task 5: `core/storage.py` — document + index readers

**Files:**
- Modify: `core/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_storage.py
from core.storage import Storage

def test_read_index(tmp_project):
    (tmp_project / "data" / "index.md").write_text("# index\n- doc1", encoding="utf-8")
    (tmp_project / "data" / "index_system_prompt.md").write_text("# agents\n## default", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    assert "doc1" in s.read_index()
    assert "default" in s.read_system_prompts()

def test_read_document_section(tmp_project):
    docs = tmp_project / "data" / "documents"
    (docs / "acme.md").write_text("## art_7\nContent A\n## art_8\nContent B", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data", documents_dir=docs)
    content = s.read_document_sections("acme", ["art_7"])
    assert "Content A" in content
    assert "Content B" not in content

def test_read_document_missing_returns_empty(tmp_project):
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    assert s.read_document_sections("nope", ["x"]) == ""
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_storage.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `core/storage.py`**

```python
"""Read-only access to index files and raw document sections.

Documents live in `data/documents/<doc_id>.md` and use `## <section_id>` headers.
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
        sp_match = re.search(r"\*\*System prompt\*\*\s*:?\s*(.*)", block,
                             flags=re.DOTALL)
        if not sp_match:
            return None
        sp = sp_match.group(0).replace("**System prompt**", "").lstrip(": \n")
        return sp.strip()
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_storage.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/storage.py tests/test_storage.py
git commit -m "refactor(storage): read-only index + document-section reader"
```

---

## Task 6: System prompt files (`router.md`, `planner.md`, `aggregator.md`)

**Files:**
- Create: `core/prompts/router.md`
- Create: `core/prompts/planner.md`
- Create: `core/prompts/aggregator.md`

- [ ] **Step 1: Create `core/prompts/router.md`**

```markdown
# NoRag Router (SLM)

You are the NoRag Router. Your job is to read the user question, the document index, and the agent catalog, then decide:

1. Which agent is best suited to answer.
2. Which 1–3 documents/sections are relevant.

You do NOT answer the question. You only route.

## Inputs you receive

- `index.md` — catalog of documents, each with doc_id, summary, sections and keywords.
- `index_system_prompt.md` — catalog of agents with their specialization.
- The user question.

## Output — STRICT JSON

```json
{
  "agent_id": "<id from index_system_prompt.md, or 'default'>",
  "documents": [
    { "doc_id": "<id from index.md>", "sections": ["<section_id>", ...] }
  ],
  "reasoning": "<1-2 sentences>"
}
```

Rules:
- Maximum 3 documents.
- Every `doc_id` and `agent_id` MUST exist in the provided indexes.
- If nothing matches, return `agent_id: "default"` and `documents: []`.
- Output valid JSON only. No prose, no code fences.
```

- [ ] **Step 2: Create `core/prompts/planner.md`**

```markdown
# NoRag Multi_L Planner (SLM)

You are the NoRag Planner. You decompose a question into N parallel L1 layers. Each layer = `(agent_id, sub-question, index_scope)`.

## Presets

- **A — Multi-Agent** : same question, different agents (perspectives croisées).
- **B — Decomposition** : split the question into sub-questions for the same/similar agent.
- **C — Multi-Corpus** : same question, different agents, different `index_scope`.
- **D — Hybrid / Auto** : you freely combine the 3 dimensions.

## Inputs

- `index.md`, `index_system_prompt.md`, user question, preset hint (`A|B|C|D`), `max_layers`.

## Output — STRICT JSON

```json
{
  "preset_used": "A",
  "reasoning": "<short>",
  "layers": [
    { "agent_id": "<id>", "question": "<text>", "index_scope": "all" }
  ]
}
```

Rules:
- `len(layers)` ≤ `max_layers`.
- Every `agent_id` MUST exist in `index_system_prompt.md`.
- `index_scope` is either `"all"` or a doc_id / tag from `index.md`.
- If preset is `D` or absent, pick freely based on the question.
- Output valid JSON only.
```

- [ ] **Step 3: Create `core/prompts/aggregator.md`**

```markdown
# NoRag Multi_L Aggregator (LLM)

You receive N independent L1 answers. Synthesize them into a single coherent response.

## Rules

1. Do NOT paraphrase lazily. Integrate insights.
2. Explicitly name contradictions between layers ("Le layer juriste et le layer technique divergent sur…").
3. Preserve ALL citations from source layers in `[doc_id, section]` format.
4. Structure:
   - Preset A → by perspective (one heading per agent).
   - Preset B → by sub-question.
   - Preset C → by corpus.
   - Preset D → choose the most natural structure.
5. End with a short "Synthèse" paragraph.

## Inputs

- The original question.
- An array of `{ agent_id, answer, documents_used }` objects.
- The `preset_used`.

Output markdown text (no JSON).
```

- [ ] **Step 4: Commit**

```bash
git add core/prompts/
git commit -m "feat(prompts): router + planner + aggregator system prompts"
```

---

## Task 7: Seed `data/index.md` and `data/index_system_prompt.md`

**Files:**
- Modify: `data/index.md`
- Create: `data/index_system_prompt.md`
- Create: `data/documents/.gitkeep`

- [ ] **Step 1: Inspect current `data/index.md` content**

Run: `head -50 data/index.md`
Keep existing catalog content if present; otherwise overwrite with seed below.

- [ ] **Step 2: If empty, seed `data/index.md`**

```markdown
# NoRag Document Index

Chaque entrée décrit un document et ses sections (chapitres, articles, annexes).
Format :

## <doc_id>
- **Titre** : <titre lisible>
- **Résumé** : <2-3 lignes>
- **Sections** :
  - `<section_id>` — <titre section> — mots-clés : ...

---

## exemple_doc
- **Titre** : Document d'exemple
- **Résumé** : Document de démonstration, à remplacer par vos ingestions.
- **Sections** :
  - `intro` — Introduction — mots-clés : aperçu, contexte
  - `conclusion` — Conclusion — mots-clés : synthèse, suite
```

- [ ] **Step 3: Create `data/index_system_prompt.md`**

```markdown
# NoRag Agent Catalog

Chaque entrée = un agent réutilisable. Le Router lit ce fichier pour choisir.

## default
**Description** : agent généraliste de fallback.
**Quand l'utiliser** : si aucun agent spécialisé ne matche, ou question floue.
**System prompt** :
> Tu es un assistant documentaire rigoureux. Tu réponds uniquement à partir
> des documents fournis, en citant chaque affirmation au format
> `[doc_id, section]`. Si l'information manque, dis-le explicitement.

## juriste_conformite
**Description** : expert juridique contrats, RGPD, conformité B2B.
**Quand l'utiliser** : clauses contractuelles, SLA, DPA, rétention données.
**System prompt** :
> Tu es juriste senior spécialisé conformité B2B. Tu réponds avec précision,
> en citant systématiquement article/section au format `[doc_id, section]`.
> Tu distingues clairement obligation, recommandation et pratique de marché.

## analyste_technique
**Description** : expert architecture et sécurité applicative.
**Quand l'utiliser** : stack, sécurité, performance, intégration API.
**System prompt** :
> Tu es architecte technique senior. Tu réponds avec précision technique,
> en citant `[doc_id, section]`. Tu identifies les risques et dépendances.

## analyste_finance
**Description** : expert analyse financière et stratégie.
**Quand l'utiliser** : macro, marchés, modèles économiques, stratégie.
**System prompt** :
> Tu es analyste financier senior. Tu réponds avec rigueur chiffrée,
> citations `[doc_id, section]`, et tu distingues fait vs interprétation.
```

- [ ] **Step 4: Create `data/documents/.gitkeep`**

```bash
touch data/documents/.gitkeep
```

- [ ] **Step 5: Commit**

```bash
git add data/index.md data/index_system_prompt.md data/documents/.gitkeep
git commit -m "feat(data): seed index.md + agent catalog"
```

---

## Task 8: `api/schemas.py` — Pydantic request/response models

**Files:**
- Create: `api/schemas.py`
- Create: `tests/test_schemas.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_schemas.py
import pytest
from pydantic import ValidationError
from api.schemas import QueryRequest, RouterOutput, PlannerOutput, LayerPlan

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
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_schemas.py -v`
Expected: FAIL.

- [ ] **Step 3: Create `api/schemas.py`**

```python
"""Pydantic request/response schemas."""

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
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_schemas.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api/schemas.py tests/test_schemas.py
git commit -m "feat(api): Pydantic schemas for L1 + MultiL I/O"
```

---

## Task 9: `core/l1_engine.py` — Router + Answer

**Files:**
- Create: `core/l1_engine.py`
- Create: `tests/test_l1_engine.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_l1_engine.py
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
        "## default\n**System prompt**:\n> Be helpful.\n", encoding="utf-8"
    )
    (tmp_project / "data" / "documents" / "doc1.md").write_text(
        "## s1\nRelevant content here.\n", encoding="utf-8"
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
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_l1_engine.py -v`
Expected: FAIL (module missing).

- [ ] **Step 3: Implement `core/l1_engine.py`**

```python
"""L1 engine: Router (SLM) + Answer (LLM) = 2 calls."""

import time
from dataclasses import dataclass
from pathlib import Path

from api.schemas import RouterOutput, DocumentRef, L1Result
from core.config import Config
from core.llm_client import LLMClient
from core.storage import Storage


@dataclass
class L1Engine:
    config: Config
    storage: Storage
    llm: LLMClient = None

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

        agent_prompt = self.storage.extract_agent_prompt(route.agent_id) or \
                       self.storage.extract_agent_prompt("default") or \
                       "You are a helpful documentary assistant. Cite [doc_id, section]."

        doc_context_parts: list[str] = []
        for d in route.documents:
            text = self.storage.read_document_sections(d.doc_id, d.sections)
            if text:
                doc_context_parts.append(f"# {d.doc_id}\n{text}")
        doc_context = "\n\n".join(doc_context_parts) or "(no documents selected)"

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
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_l1_engine.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/l1_engine.py tests/test_l1_engine.py
git commit -m "feat(core): L1 engine (Router + Answer)"
```

---

## Task 10: `core/multi_l_engine.py` — Planner + parallel L1 + Aggregator

**Files:**
- Create: `core/multi_l_engine.py`
- Create: `tests/test_multi_l_engine.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_multi_l_engine.py
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
        "## default\n**System prompt**:\n> x\n## juriste\n**System prompt**:\n> y\n",
        encoding="utf-8",
    )
    return tmp_project

@pytest.mark.asyncio
async def test_multi_l_runs_three_layers(seeded):
    cfg = Config(project_root=seeded)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = MultiLEngine(config=cfg, storage=storage)

    planner_return = (
        {
            "preset_used": "A",
            "reasoning": "perspectives",
            "layers": [
                {"agent_id": "default", "question": "q", "index_scope": "all"},
                {"agent_id": "juriste", "question": "q", "index_scope": "all"},
            ],
        },
        LLMResponse(text="{}", tokens=200),
    )

    fake_l1 = L1Result(
        agent_id="default",
        documents_used=[DocumentRef(doc_id="doc1", sections=["s1"])],
        answer="layer answer",
        tokens={"router": 50, "answer": 100},
        latency_ms=10,
    )

    aggregator_return = LLMResponse(text="# Synthèse\nfinal [doc1, s1]", tokens=500)

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=planner_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=aggregator_return)), \
         patch.object(engine.l1, "run",
                      new=AsyncMock(return_value=fake_l1)):
        result = await engine.run(question="q")

    assert result.preset_used == "A"
    assert len(result.layers) == 2
    assert "final" in result.aggregated_answer
    assert result.tokens["planner"] == 200
    assert result.tokens["aggregator"] == 500
    assert result.tokens["layers_total"] == (50 + 100) * 2

@pytest.mark.asyncio
async def test_multi_l_caps_layers_at_max(seeded, monkeypatch):
    monkeypatch.setenv("MULTIL_MAX_LAYERS", "2")
    cfg = Config(project_root=seeded)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    engine = MultiLEngine(config=cfg, storage=storage)

    planner_return = (
        {"preset_used": "A", "reasoning": "x",
         "layers": [
             {"agent_id": "default", "question": "q", "index_scope": "all"},
             {"agent_id": "juriste", "question": "q", "index_scope": "all"},
             {"agent_id": "default", "question": "q", "index_scope": "all"},
         ]},
        LLMResponse(text="{}", tokens=10),
    )

    fake_l1 = L1Result(
        agent_id="x", documents_used=[], answer="a",
        tokens={"router": 1, "answer": 1}, latency_ms=1,
    )

    with patch.object(engine.llm, "generate_json",
                      new=AsyncMock(return_value=planner_return)), \
         patch.object(engine.llm, "generate",
                      new=AsyncMock(return_value=LLMResponse(text="agg", tokens=1))), \
         patch.object(engine.l1, "run",
                      new=AsyncMock(return_value=fake_l1)) as l1_mock:
        await engine.run(question="q")

    assert l1_mock.call_count == 2
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_multi_l_engine.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `core/multi_l_engine.py`**

```python
"""Multi_L engine: Planner (SLM) + N parallel L1 + Aggregator (LLM)."""

import asyncio
import time
from dataclasses import dataclass

from api.schemas import (
    PlannerOutput, LayerPlan, LayerResult, MultiLResult, L1Result, DocumentRef,
)
from core.config import Config
from core.l1_engine import L1Engine
from core.llm_client import LLMClient
from core.storage import Storage


@dataclass
class MultiLEngine:
    config: Config
    storage: Storage
    llm: LLMClient = None
    l1: L1Engine = None

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
            except (asyncio.TimeoutError, Exception):
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
        aggregator_user = self._format_layers_for_aggregator(question, plan.preset_used, layer_results)

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

    def _format_layers_for_aggregator(self, question: str, preset: str,
                                       layers: list[LayerResult]) -> str:
        blocks = [f"# Question\n{question}\n", f"# preset_used\n{preset}\n"]
        for i, l in enumerate(layers, 1):
            docs = ", ".join(f"[{d.doc_id}, {'/'.join(d.sections)}]" for d in l.documents_used)
            blocks.append(f"## Layer {i} — agent={l.agent_id}\nDocs: {docs}\n\n{l.answer}")
        return "\n\n".join(blocks)
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_multi_l_engine.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/multi_l_engine.py tests/test_multi_l_engine.py
git commit -m "feat(core): Multi_L engine (Planner + parallel L1 + Aggregator)"
```

---

## Task 11: `core/indexer.py` — archivist ingestion

**Files:**
- Modify: `core/indexer.py`
- Create: `tests/test_indexer.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_indexer.py
import pytest
from unittest.mock import AsyncMock, patch
from core.config import Config
from core.storage import Storage
from core.indexer import Indexer
from core.llm_client import LLMResponse

@pytest.mark.asyncio
async def test_ingest_appends_card_to_index_and_writes_document(tmp_project):
    cfg = Config(project_root=tmp_project)
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)
    (cfg.index_path).write_text("# NoRag Document Index\n", encoding="utf-8")

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
    assert "new_doc" in cfg.index_path.read_text(encoding="utf-8")
    assert (cfg.documents_dir / "new_doc.md").exists()
    assert "Contenu brut" in (cfg.documents_dir / "new_doc.md").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_indexer.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `core/indexer.py`**

```python
"""Archivist ingestion: raw text → (index card, document file)."""

from dataclasses import dataclass

from core.config import Config
from core.llm_client import LLMClient
from core.storage import Storage


ARCHIVIST_SYSTEM = """Tu es l'Archiviste NoRag. À partir d'un texte brut, tu produis :
1. Une fiche d'index au format exact attendu dans `index.md`.
2. Le document structuré en sections `## <section_id>` (contenu complet, pas de chunking).

Format de sortie STRICT :

## <doc_id>
- **Titre** : ...
- **Résumé** : ...
- **Sections** :
  - `<section_id>` — <titre section> — mots-clés : ...

---DOCUMENT---
## <section_id_1>
<contenu complet de la section>

## <section_id_2>
<contenu complet>

Règles :
- `<doc_id>` reçu en paramètre utilisateur, à reprendre tel quel.
- Sections courtes mais complètes (jamais de chunking arbitraire).
- Aucun texte hors des deux blocs.
"""


@dataclass
class Indexer:
    config: Config
    storage: Storage
    llm: LLMClient = None

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMClient(api_key=self.config.gemini_api_key)

    async def ingest(self, doc_id: str, raw_text: str) -> dict:
        user = f"# doc_id\n{doc_id}\n\n# texte brut\n{raw_text}\n"
        resp = await self.llm.generate(
            model=self.config.answer_model,
            system=ARCHIVIST_SYSTEM,
            user=user,
        )
        if "---DOCUMENT---" not in resp.text:
            raise ValueError("Archivist response missing ---DOCUMENT--- separator")

        card, document = resp.text.split("---DOCUMENT---", 1)
        card = card.strip()
        document = document.strip()

        existing = self.config.index_path.read_text(encoding="utf-8") if self.config.index_path.exists() else ""
        if not existing.endswith("\n"):
            existing += "\n"
        self.config.index_path.write_text(existing + "\n" + card + "\n", encoding="utf-8")

        doc_path = self.config.documents_dir / f"{doc_id}.md"
        doc_path.write_text(document + "\n", encoding="utf-8")

        return {"doc_id": doc_id, "tokens": resp.tokens}
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_indexer.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add core/indexer.py tests/test_indexer.py
git commit -m "refactor(indexer): archivist one-shot ingestion (card + document)"
```

---

## Task 12: `api/main.py` — FastAPI entrypoint

**Files:**
- Modify: `api/main.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_api.py
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from api.main import create_app
from api.schemas import L1Result, MultiLResult, DocumentRef, LayerResult

@pytest.fixture
def seeded_app(tmp_project, monkeypatch):
    (tmp_project / "data" / "index.md").write_text("## doc1\n", encoding="utf-8")
    (tmp_project / "data" / "index_system_prompt.md").write_text(
        "## default\n**System prompt**:\n> x\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_project)
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    app = create_app(project_root=tmp_project)
    return app

def test_query_defaults_to_l1(seeded_app):
    fake = L1Result(agent_id="default", documents_used=[], answer="ok",
                    tokens={"router": 1, "answer": 1}, latency_ms=1)
    with patch("api.main.L1Engine.run", new=AsyncMock(return_value=fake)):
        client = TestClient(seeded_app)
        r = client.post("/query", json={"question": "hi"})
    assert r.status_code == 200
    assert r.json()["mode"] == "L1"

def test_query_multil_override(seeded_app):
    fake = MultiLResult(
        preset_used="A", layers=[], aggregated_answer="agg",
        tokens={"planner": 1, "layers_total": 1, "aggregator": 1}, latency_ms=1,
    )
    with patch("api.main.MultiLEngine.run", new=AsyncMock(return_value=fake)):
        client = TestClient(seeded_app)
        r = client.post("/query", json={"question": "hi", "mode": "MultiL"})
    assert r.status_code == 200
    assert r.json()["mode"] == "MultiL"

def test_index_rebuild_returns_stats(seeded_app):
    client = TestClient(seeded_app)
    r = client.get("/documents")
    assert r.status_code == 200
    assert "documents" in r.json()
```

- [ ] **Step 2: Run test**

Run: `pytest tests/test_api.py -v`
Expected: FAIL.

- [ ] **Step 3: Rewrite `api/main.py`**

```python
"""FastAPI entrypoint. Exposes /query, /documents, /ingest."""

from pathlib import Path
from fastapi import FastAPI, HTTPException

from api.schemas import QueryRequest, L1Result, MultiLResult
from core.config import Config
from core.storage import Storage
from core.l1_engine import L1Engine
from core.multi_l_engine import MultiLEngine
from core.indexer import Indexer


def create_app(project_root: Path | None = None) -> FastAPI:
    cfg = Config(project_root=project_root) if project_root else Config()
    storage = Storage(data_dir=cfg.data_dir, documents_dir=cfg.documents_dir)

    app = FastAPI(title="NoRag", version="2.0")

    @app.post("/query", response_model=dict)
    async def query(req: QueryRequest):
        mode = req.mode or cfg.default_mode
        if mode == "L1":
            engine = L1Engine(config=cfg, storage=storage)
            result: L1Result = await engine.run(
                question=req.question,
                agent_forced=req.agent_hint,
                index_scope=req.index_scope,
            )
            return result.model_dump()
        elif mode == "MultiL":
            engine = MultiLEngine(config=cfg, storage=storage)
            result: MultiLResult = await engine.run(
                question=req.question,
                preset=req.preset,
                max_layers=req.max_layers,
            )
            return result.model_dump()
        raise HTTPException(status_code=400, detail=f"Unknown mode: {mode}")

    @app.post("/ingest")
    async def ingest(doc_id: str, raw_text: str):
        indexer = Indexer(config=cfg, storage=storage)
        return await indexer.ingest(doc_id=doc_id, raw_text=raw_text)

    @app.get("/documents")
    def list_documents():
        docs = [p.stem for p in cfg.documents_dir.glob("*.md")]
        return {"documents": docs}

    return app


app = create_app()
```

- [ ] **Step 4: Run test**

Run: `pytest tests/test_api.py -v`
Expected: PASS.

- [ ] **Step 5: Smoke-test the server**

Run: `uvicorn api.main:app --reload`
Expected: server starts, `/docs` reachable in browser. Stop with Ctrl+C.

- [ ] **Step 6: Commit**

```bash
git add api/main.py tests/test_api.py
git commit -m "feat(api): /query with L1/MultiL + /ingest + /documents"
```

---

## Task 13: `api/__init__.py` + ensure package imports work

**Files:**
- Verify: `api/__init__.py`, `core/__init__.py` are present and valid.

- [ ] **Step 1: Ensure both files exist**

```bash
[ -f api/__init__.py ] || touch api/__init__.py
[ -f core/__init__.py ] || touch core/__init__.py
```

- [ ] **Step 2: Run full test suite**

Run: `pytest -q`
Expected: ALL PASS.

- [ ] **Step 3: Commit if anything changed**

```bash
git add -A && git diff --cached --quiet || git commit -m "chore: ensure package __init__ files"
```

---

## Task 14: Update `norag/plugins/*.md` to L1 flow

**Files:**
- Modify: `norag/plugins/claude.md`, `gpt.md`, `gemini.md`, `grok.md` (create any missing)

- [ ] **Step 1: Inspect existing plugin files**

Run: `ls norag/plugins/`

- [ ] **Step 2: For each provider, write/replace with the canonical L1 prompt**

Template (same body, rename file per provider):

```markdown
# NoRag — L1 System Prompt (pour chat web)

Tu es un agent NoRag. L'utilisateur va te fournir :
1. `index.md` — catalogue des documents.
2. `index_system_prompt.md` — catalogue des agents.
3. Les contenus bruts des documents à référencer.

## Ton pipeline (2 étapes, SILENCIEUX)

**Étape 1 — Routage** : tu identifies (a) l'agent approprié dans `index_system_prompt.md`, (b) les 1–3 sections de documents pertinentes dans `index.md`.

**Étape 2 — Réponse** : tu adoptes le system prompt de l'agent choisi et réponds en citant OBLIGATOIREMENT au format `[doc_id, section]`.

## Règles

- Jamais de réponse sans citation.
- Si aucun document ne couvre la question : dis-le explicitement, ne devine pas.
- Pour ingérer un nouveau doc : l'utilisateur te dira `/archive <texte>` — tu réponds avec une fiche au format `## <doc_id>\n- **Titre**...\n- **Résumé**...\n- **Sections**...` + le document structuré en `## <section_id>`.

Multi_L n'est pas disponible en mode chat web (réservé à l'API).
```

Write the same content to:
- `norag/plugins/claude.md`
- `norag/plugins/gpt.md`
- `norag/plugins/gemini.md`
- `norag/plugins/grok.md`

- [ ] **Step 3: Commit**

```bash
git add norag/plugins/
git commit -m "docs(plugins): align web-chat prompts with L1 pipeline"
```

---

## Task 15: Rewrite `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace `README.md` with the new version**

```markdown
# NoRag v3 — L1 & Multi_L

NoRag is a document Q&A system that **replaces RAG vector embeddings with LLM-driven routing over Markdown indexes**. Two explicit pipelines:

- **L1** — 2 LLM calls: a Router (SLM) selects documents + agent, an Answerer (LLM) generates the response.
- **Multi_L** — a Planner decomposes the question into N parallel L1 layers; an Aggregator synthesizes.

## Why NoRag beats RAG

| Criterion | RAG | NoRag |
|---|---|---|
| Infra | Vector DB + embeddings | Markdown files |
| Cost to add a doc | Recurring (re-embed, vector storage) | One-shot (archivist pass) |
| Context fed to LLM | Arbitrary chunks | Full sections |
| Auditability | Opaque vectors | Git-diffable Markdown |
| Citations | Approximate | Precise `[doc_id, section]` |

Details: [ANALYSE_NORAG_VS_RAG.md](ANALYSE_NORAG_VS_RAG.md), [The NoRag Blueprint](The_NoRag_Blueprint.pdf).

## Quick start

```bash
git clone <repo> && cd NoRag
pip install -r requirements.txt
cp .env.example .env   # fill GEMINI_API_KEY
uvicorn api.main:app --reload
```

API at `http://localhost:8000/docs`.

### Query L1 (default)

```bash
curl -X POST localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question": "Quelle est la SLA prévue au contrat Acme ?"}'
```

### Query Multi_L

```bash
curl -X POST localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question": "Compare AWS et Azure sur la sécurité", "mode": "MultiL", "preset": "B"}'
```

### Ingest a document

```bash
curl -X POST 'localhost:8000/ingest?doc_id=acme_contract' \
  -H 'content-type: application/json' \
  -d '"<raw text of the document...>"'
```

## Configuration

See `.env.example`. Key variables:

- `GEMINI_API_KEY` — required.
- `ROUTER_MODEL` — SLM used for Router + Planner (cheap, fast).
- `ANSWER_MODEL` / `AGGREGATOR_MODEL` — strong LLMs.
- `DEFAULT_MODE` — `L1` or `MultiL`.
- `MULTIL_MAX_LAYERS`, `MULTIL_LAYER_TIMEOUT_S`.

## Project layout

```
NoRag/
├── core/
│   ├── config.py              # typed settings
│   ├── llm_client.py          # async Gemini wrapper
│   ├── l1_engine.py           # Router + Answer
│   ├── multi_l_engine.py      # Planner + parallel L1 + Aggregator
│   ├── indexer.py             # archivist ingestion
│   ├── storage.py             # read index + document sections
│   └── prompts/
│       ├── router.md
│       ├── planner.md
│       └── aggregator.md
├── data/
│   ├── index.md               # document catalog
│   ├── index_system_prompt.md # agent catalog
│   └── documents/             # raw doc markdowns
├── api/
│   ├── main.py                # FastAPI app
│   └── schemas.py             # Pydantic models
└── norag/plugins/             # copy-paste prompts for web chats
```

## Use modes

- **API** — `uvicorn api.main:app`, full L1 + Multi_L.
- **Web chat (L1 only)** — copy `norag/plugins/<provider>.md` into your LLM's system prompt and paste `data/index.md` + `data/index_system_prompt.md` + the documents you want searchable.

## Tests

```bash
pytest -q
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for L1 + Multi_L architecture"
```

---

## Task 16: Final verification pass

- [ ] **Step 1: Run full test suite**

Run: `pytest -q`
Expected: all green.

- [ ] **Step 2: Boot API and hit each endpoint**

Run: `uvicorn api.main:app --reload` in one terminal, then in another:

```bash
curl localhost:8000/documents
curl -X POST localhost:8000/query -H 'content-type: application/json' \
  -d '{"question": "test"}'
```

Expected: both return 200 (the `/query` call may fail on LLM call if no credit — that's OK, we're verifying wiring). Stop the server.

- [ ] **Step 3: Check `git status` clean**

Run: `git status`
Expected: clean tree (or only intentional env files untracked).

- [ ] **Step 4: Tag the release**

```bash
git tag -a v3.0-backend -m "NoRag v3: L1 + Multi_L backend"
```

---

## Self-review results

- **Spec coverage**: §2 tiering → Task 3; §3 L1 → Task 9; §4 Multi_L → Task 10; §5 presets → prompt `planner.md` in Task 6; §6 argument → Task 15 README; §7 file tree → Tasks 1, 7, 11, 12; §8 microsite → separate plan; §9 order → tasks numbered in order.
- **Placeholders**: none.
- **Type consistency**: `RouterOutput`, `PlannerOutput`, `LayerPlan`, `LayerResult`, `L1Result`, `MultiLResult`, `DocumentRef` defined once in `api/schemas.py`, imported consistently.
