# NoRag — L1 / Multi_L + Microsite — Design Spec

**Date** : 2026-04-23
**Auteur** : brainstorm GOMES + Claude
**Statut** : approuvé, prêt pour plan d'implémentation

---

## 1. Contexte et objectifs

Le repo `NoRag` implémente aujourd'hui un système Q&A documentaire à 3 index Markdown (`index_agents.md`, `index_documents.md`, `index_history.md`) opéré via FastAPI. L'architecture actuelle mélange routage, sélection d'agent et historique, et n'expose pas de mode "multi-perspective".

Objectifs de ce refactor :

1. **Simplifier** en 2 logiques distinctes et explicites : **L1** (minimal, 2 appels LLM) et **Multi_L** (N × L1 en parallèle + agrégation).
2. **Réduire les coûts** via tiering de modèles (SLM pour routage, LLM fort pour réponse/synthèse).
3. **Nettoyer** les fichiers de présentation redondants et consolider la documentation dans un **microsite Next.js**.
4. **Conserver** les avantages NoRag vs RAG : simplicité, coût d'ingestion one-shot, fiabilité (documents complets donnés au LLM).

---

## 2. Architecture d'ensemble

```
         POST /query { mode: "L1" | "MultiL" }
                        │
              ┌─────────┴─────────┐
              │ Mode résolu       │  (défaut config + override requête)
              └─────────┬─────────┘
          ┌─────────────┴─────────────┐
          ▼                           ▼
   ┌────────────┐             ┌──────────────────┐
   │ L1 ENGINE  │             │ MULTI_L ENGINE   │
   │ Call 1     │             │ Planner (SLM)    │
   │  Router    │             │      │           │
   │  (SLM)     │             │      ▼           │
   │ Call 2     │             │ N × L1 parallèle │
   │  Answer    │             │      │           │
   │  (LLM)     │             │      ▼           │
   └────────────┘             │ Aggregator (LLM) │
                              └──────────────────┘
```

### Principes

- **L1 = brique atomique** : 2 appels, stateless.
- **Multi_L = orchestrateur** paramétré par 3 dimensions `(agent_id, question, index_scope)` → couvre 4 presets (voir §5).
- **Mode par défaut** configurable (`.env` `DEFAULT_MODE`), overridable par requête.
- **Historique optionnel** (non obligatoire, activable par session en phase 2).
- **Un seul provider LLM initial** : Gemini. Abstrait derrière `LLMClient` pour extensions futures.

### Tiering des modèles

Configurable dans `.env` :

```
ROUTER_MODEL=gemini-flash-lite       # SLM : classifier / router / planner
ANSWER_MODEL=gemini-2.5-pro          # LLM fort : raisonnement / réponse
AGGREGATOR_MODEL=gemini-2.5-pro      # LLM fort : synthèse multi-layer
DEFAULT_MODE=L1                      # L1 | MultiL
MULTIL_MAX_LAYERS=3
MULTIL_LAYER_TIMEOUT_S=30
```

---

## 3. Pipeline L1

### Entrée

```json
POST /query
{
  "question": "...",
  "mode": "L1",
  "agent_hint": null,        // optionnel
  "index_scope": null        // optionnel
}
```

### Appel 1 — Router (SLM)

**Contexte envoyé** :
- `core/prompts/router.md` (system)
- `data/index.md` (catalogue docs)
- `data/index_system_prompt.md` (catalogue agents)
- Question utilisateur

**Sortie JSON strict** (validée Pydantic) :

```json
{
  "agent_id": "juriste_conformite",
  "documents": [
    { "doc_id": "contrat_saas_vendor_acme", "sections": ["art_7", "annexe_B"] },
    { "doc_id": "politique_dpo_interne_2024", "sections": ["s2-retention"] }
  ],
  "reasoning": "Question conformité contractuelle → juriste + clauses rétention"
}
```

Si parse JSON échoue : 1 retry. Si échoue encore : fallback `agent_id="default"`, sélection top-3 docs par mots-clés simples.

### Appel 2 — Answer (LLM fort)

**Contexte envoyé** :
- System prompt = entrée `agent_id` de `index_system_prompt.md`
- Contenu brut des sections sélectionnées (lu depuis `data/documents/`)
- Question utilisateur

**Sortie** : réponse texte avec citations obligatoires `[doc_id, section]`.

### Format `index_system_prompt.md`

```markdown
# Catalogue d'agents

## juriste_conformite
**Description** : expert juridique contrats, RGPD, conformité
**Quand l'utiliser** : clauses contractuelles, rétention, DPA, SLA
**System prompt** :
> Tu es juriste senior spécialisé conformité B2B. Tu réponds avec
> précision, en citant article/section au format [Doc, Section]...

## analyste_technique
**Description** : expert architecture et sécurité applicative
...

## default
**Description** : agent généraliste de fallback
```

Le Router lit ce fichier en texte clair (comme `index.md`) pour choisir l'agent — pas de config dupliquée.

### Réponse API

```json
{
  "mode": "L1",
  "agent_id": "juriste_conformite",
  "documents_used": [...],
  "answer": "La rétention est fixée à 90 jours [contrat_saas_vendor_acme, art_7]...",
  "tokens": { "router": 780, "answer": 2950 },
  "latency_ms": 1620
}
```

---

## 4. Pipeline Multi_L

### Entrée

```json
POST /query
{
  "question": "...",
  "mode": "MultiL",
  "preset": "A" | "B" | "C" | "D",   // défaut: "D" (auto)
  "max_layers": 3,
  "agent_hint": null,
  "index_scope": null
}
```

### Étape 1 — Planner (SLM)

**Contexte envoyé** :
- `core/prompts/planner.md` (system, documente les 4 presets)
- `data/index.md`
- `data/index_system_prompt.md`
- Question + preset demandé (ou "auto")

**Sortie JSON strict** :

```json
{
  "preset_used": "A",
  "reasoning": "Question stratégique nécessitant perspectives juridique + tech + finance",
  "layers": [
    { "agent_id": "juriste_conformite", "question": "<Q>", "index_scope": "all" },
    { "agent_id": "analyste_technique", "question": "<Q>", "index_scope": "all" },
    { "agent_id": "analyste_finance",   "question": "<Q>", "index_scope": "all" }
  ]
}
```

Contraintes : `len(layers) ≤ max_layers`, chaque `agent_id` doit exister dans `index_system_prompt.md`.

### Étape 2 — Exécution parallèle

```python
results = await asyncio.gather(*[
    l1_engine.run(
        q=layer.question,
        agent_forced=layer.agent_id,
        index_scope=layer.index_scope
    )
    for layer in plan.layers
], return_exceptions=True)
```

Timeout par layer = `MULTIL_LAYER_TIMEOUT_S`. Layer en échec → exclu de l'agrégation, log warn, Aggregator tourne avec les layers restants (si ≥ 1).

### Étape 3 — Aggregator (LLM fort)

**Contexte envoyé** :
- `core/prompts/aggregator.md` (system)
- Question originale
- Les N réponses L1 avec métadonnées `{agent_id, answer, documents_used}`

**Rôle** :
- Synthèse structurée, pas paraphrase
- Nommage explicite des contradictions entre layers
- Conservation de toutes les citations des layers sources
- Structuration par perspective (preset A) ou par sous-question (preset B) ou par corpus (preset C)

### Réponse API

```json
{
  "mode": "MultiL",
  "preset_used": "A",
  "layers": [
    { "agent_id": "...", "answer": "...", "documents_used": [...] },
    ...
  ],
  "aggregated_answer": "Synthèse finale avec toutes citations...",
  "tokens": { "planner": 950, "layers_total": 12400, "aggregator": 4200 },
  "latency_ms": 4800
}
```

---

## 5. Presets Multi_L

Même moteur, setup différent décidé par le Planner :

### Preset A — Multi-Agent (perspectives croisées)

```
Question: "Faut-il lancer le produit X en Europe ?"
Layers:
  L1: (agent="juriste",   q=Q, index_scope=all)
  L2: (agent="finance",   q=Q, index_scope=all)
  L3: (agent="marketing", q=Q, index_scope=all)
Aggregator: synthèse multi-perspective
```

### Preset B — Décomposition (questions complexes)

```
Question: "Compare la stratégie cloud d'AWS et d'Azure sur 2020-2024"
Layers:
  L1: (agent="analyste", q="Stratégie cloud AWS 2020-2024",   scope=auto)
  L2: (agent="analyste", q="Stratégie cloud Azure 2020-2024", scope=auto)
Aggregator: comparaison structurée
```

### Preset C — Multi-Corpus

```
Question: "Que disent nos contrats clients et notre doc technique sur la SLA ?"
Layers:
  L1: (agent="juriste", q=Q, index_scope="contrats")
  L2: (agent="tech",    q=Q, index_scope="doc_technique")
Aggregator: réponse unifiée
```

### Preset D — Hybride (auto)

Le Planner décide librement de varier les 3 dimensions. Par défaut si preset absent de la requête.

---

## 6. Argumentaire NoRag vs RAG

À intégrer dans `README.md` et dans la section 2 du microsite.

### Simplicité (zéro infra vectorielle)

| RAG classique | NoRag |
|---|---|
| Embeddings model + vector DB (Pinecone/Weaviate/Qdrant) | Fichiers Markdown lisibles |
| Chunking strategy + overlap tuning | Sections définies une fois à l'ingestion |
| Reranker à configurer | Le Router LLM fait le tri |
| Pipeline ML à maintenir | `git diff` sur `index.md` |

### Coût maîtrisé à l'ingestion

- **RAG** : chaque doc = re-embed (payant) + re-index + vector search payée à chaque requête.
- **NoRag** : 1 appel LLM "Archiviste" par doc → fiche Markdown. **Payé une fois.** Le Router relit `index.md` (quelques milliers de tokens, cachables).

Scénario 1000 docs : `index.md` ≈ 200-500 KB, tient dans contexte SLM (1M tokens Gemini Flash). Coût routing ≈ 0,001 €/requête.

### Fiabilité (documents complets)

- **RAG** : chunks 500-1000 tokens découpés arbitrairement → LLM hallucine pour combler.
- **NoRag** : section complète (chapitre/article/annexe) → cohérence interne préservée, citations `[Doc, Section]` vérifiables humainement.

### Tableau récap

| Critère | RAG | NoRag |
|---|---|---|
| Infra | Vector DB + embeddings | Fichiers MD |
| Coût d'ajout doc | Récurrent | One-shot |
| Contexte LLM | Chunks tronqués | Sections complètes |
| Auditabilité | Opaque (vecteurs) | Transparent (git-diffable) |
| Citations | Approximatives | Précises et vérifiables |
| Correction index | Data scientist | Tout dev lisant du MD |

---

## 7. Arborescence finale

```
NoRag/
├── README.md                       # réécrit L1 + Multi_L + argumentaire
├── requirements.txt
├── .env.example                    # + ROUTER_MODEL, ANSWER_MODEL, AGGREGATOR_MODEL, DEFAULT_MODE
├── .gitignore
│
├── ANALYSE_NORAG_VS_RAG.md         # gardé
├── The_NoRag_Blueprint.pdf         # gardé
│
├── data/
│   ├── index.md                    # catalogue docs
│   ├── index_system_prompt.md      # catalogue agents
│   └── documents/                  # textes bruts
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── llm_client.py               # abstraction Gemini
│   ├── indexer.py                  # ingestion → index.md
│   ├── storage.py
│   ├── l1_engine.py                # Router + Answer
│   ├── multi_l_engine.py           # Planner + N×L1 + Aggregator
│   └── prompts/
│       ├── router.md
│       ├── planner.md
│       └── aggregator.md
│
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI /query /index /documents
│   └── schemas.py                  # Pydantic
│
├── norag/
│   └── plugins/                    # prompts LLM web mis à jour (L1 uniquement)
│       ├── claude.md
│       ├── gpt.md
│       ├── gemini.md
│       └── grok.md
│
└── site/                           # microsite Next.js
    ├── package.json
    ├── next.config.js
    ├── tailwind.config.ts
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    ├── components/
    │   ├── Hero.tsx
    │   ├── L1Demo.tsx
    │   ├── MultiLDemo.tsx
    │   ├── Presets.tsx
    │   └── Footer.tsx
    └── public/
        └── blueprint.pdf
```

### Suppressions

- `pres_simple_*.{html,pptx,pdf}`, `pres_complet_*.pptx`, `pres_full_*.html`
- `PRESENTATION_COMMERCIALE.md`, `PRESENTATION_EXECUTIVE.md`
- `NoRag_Archiviste.md`
- `data/index_agents.md`, `data/index_history.md`
- `api/local_query.py`, `api/gemini.py`, `api/backend/`, `api/routes/`
- `core/index_builder.py` (fusionné dans `indexer.py`)

---

## 8. Microsite Next.js

### Stack

- Next.js 15 App Router + TypeScript
- Tailwind CSS v4
- Framer Motion (animations de démos)
- Shiki (syntax highlighting)
- **Export statique** (`next build && next export`) → pas de backend, pas de démo live

### Structure (scroll unique)

1. **Hero** — slogan "NoRag. RAG without vectors." + 2 CTA
2. **Why not RAG** — tableau 3 axes (simplicité, coût, fiabilité)
3. **How it works — L1** — démo visuelle animée au scroll
4. **How it works — Multi_L** — démo visuelle animée au scroll
5. **Presets** — 4 cartes (A/B/C/D) avec exemples concrets
6. **Under the hood** — snippets `index.md` + `index_system_prompt.md`
7. **Get started** — 3 modes (API / CLI / Plugin LLM web) + GitHub + Blueprint PDF
8. **Footer**

### Palette

```
bg-base:    #0a0a0b
bg-surface: #131316
text:       #f5f5f7
accent:     #7c5cff    (violet signature)
accent-2:   #3ae0c8    (menthe citations)
muted:      #71717a
```

### Composants démo

- **L1Demo** : SVG Framer Motion, 3 états déclenchés par scroll (question entre → Router highlight docs dans `index.md` → Answer génère réponse avec citations).
- **MultiLDemo** : 3 layers parallèles animés puis convergence vers Aggregator.
- **Presets** : 4 cartes flip/hover montrant `question → JSON plan`.

### Contenu linkable

- `/blueprint.pdf` → copie de `The_NoRag_Blueprint.pdf`
- `/analyse` (MDX render de `ANALYSE_NORAG_VS_RAG.md`)
- `/github` → redirect repo

---

## 9. Ordre d'implémentation

1. **Nettoyage** — suppressions fichiers redondants
2. **Core engine** — `config`, `llm_client`, `indexer`, `storage`, `l1_engine`, `multi_l_engine`
3. **Prompts** — `router.md`, `planner.md`, `aggregator.md` + exemples `index_system_prompt.md`
4. **API** — refactor `api/main.py` avec `/query`, `/index/rebuild`, `/documents`
5. **Plugins** — mise à jour `norag/plugins/*.md` (L1 uniquement, Multi_L = API only)
6. **README** — réécrit
7. **Microsite** — scaffold Next.js + 8 sections + démos animées

---

## 10. Hors scope (phase 2 potentielle)

- Historique conversationnel persistant (SQLite/Supabase)
- Cache Planner sur question normalisée
- Support multi-provider (OpenAI, Anthropic, xAI) via `LLMClient`
- Démo live interactive sur le microsite
- Auto-escalation L1 → Multi_L sur confiance basse
