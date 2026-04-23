# NoRag v3 — L1 & Multi_L

NoRag is a document Q&A system that **replaces RAG vector embeddings with LLM-driven routing over Markdown indexes**. Two explicit pipelines:

- **L1** — 2 LLM calls: a Router (SLM) selects documents + agent, an Answerer (LLM) generates the response.
- **Multi_L** — a Planner decomposes the question into N parallel L1 layers; an Aggregator synthesizes.

## Why NoRag beats RAG

| Criterion | RAG | NoRag |
|---|---|---|
| Infrastructure | Vector DB + embeddings | Markdown files |
| Cost to add a doc | Recurring (re-embed, vector storage) | One-shot archivist pass |
| Context fed to LLM | Arbitrary chunks | Full sections |
| Auditability | Opaque vectors | Git-diffable Markdown |
| Citations | Approximate | Precise `[doc_id, section]` |

Full analysis: [ANALYSE_NORAG_VS_RAG.md](ANALYSE_NORAG_VS_RAG.md) — [Blueprint PDF](The_NoRag_Blueprint.pdf)

## Quick start

```bash
git clone <repo> && cd NoRag
pip install -r requirements.txt
cp .env.example .env   # fill GEMINI_API_KEY
uvicorn api.main:app --reload
```

API at `http://localhost:8000/docs`.

## Query L1 (default)

```bash
curl -X POST localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question": "Quelle est la SLA prévue dans le contrat Acme ?"}'
```

## Query Multi_L

```bash
curl -X POST localhost:8000/query \
  -H 'content-type: application/json' \
  -d '{"question": "Analyse la conformité RGPD", "mode": "MultiL", "preset": "A"}'
```

## Ingest a document

```bash
curl -X POST 'localhost:8000/ingest?doc_id=my_doc' \
  -H 'content-type: application/json' \
  -d '"<raw text of the document>"'
```

## Configuration

Key `.env` variables:

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | Required |
| `ROUTER_MODEL` | `gemini-2.5-flash-lite` | SLM for Router + Planner |
| `ANSWER_MODEL` | `gemini-2.5-pro` | LLM for Answer |
| `AGGREGATOR_MODEL` | `gemini-2.5-pro` | LLM for Aggregator |
| `DEFAULT_MODE` | `L1` | `L1` or `MultiL` |
| `MULTIL_MAX_LAYERS` | `3` | Max parallel layers |
| `MULTIL_LAYER_TIMEOUT_S` | `30` | Per-layer timeout |

## Project layout

```
NoRag/
├── core/
│   ├── config.py              # typed settings
│   ├── llm_client.py          # async Gemini wrapper
│   ├── l1_engine.py           # Router + Answer (2 calls)
│   ├── multi_l_engine.py      # Planner + N×L1 + Aggregator
│   ├── indexer.py             # archivist ingestion
│   ├── storage.py             # read index + document sections
│   └── prompts/
│       ├── router.md          # SLM Router system prompt
│       ├── planner.md         # SLM Planner system prompt
│       └── aggregator.md      # LLM Aggregator system prompt
├── data/
│   ├── index.md               # document catalog (routing)
│   ├── index_system_prompt.md # agent catalog
│   └── documents/             # <doc_id>.md files with ## sections
├── api/
│   ├── main.py                # FastAPI: /query /ingest /documents
│   └── schemas.py             # Pydantic models
└── norag/plugins/             # copy-paste prompts for web chats
```

## Use modes

- **API** — `uvicorn api.main:app`, full L1 + Multi_L.
- **Web chat (L1 only)** — copy `norag/plugins/<provider>.md` as system prompt, then paste `data/index.md` + `data/index_system_prompt.md` in your first message.
- **Claude Code skill** — copy `norag/plugins/claude_skill.md` into `~/.claude/skills/norag/SKILL.md`, then use `/norag <question>`.

## Multi_L presets

| Preset | Strategy |
|---|---|
| A | Same question, different agents (cross-perspectives) |
| B | Decomposed sub-questions, same agent |
| C | Same question, different agents, different doc scopes |
| D | Hybrid auto — Planner decides freely |

## Tests

```bash
pytest -q
```
