"use client";
import { useLang } from "@/lib/i18n";
import Link from "next/link";

/* ── tiny sub-components ── */

function Section({ id, children }: { id?: string; children: React.ReactNode }) {
  return (
    <section id={id} className="mb-20 scroll-mt-24">
      {children}
    </section>
  );
}

function H2({ children }: { children: React.ReactNode }) {
  return (
    <h2
      className="text-3xl md:text-4xl font-semibold tracking-tight mb-6 pb-4"
      style={{ borderBottom: "1px solid rgba(255,255,255,0.08)" }}
    >
      {children}
    </h2>
  );
}

function H3({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xl font-semibold mt-10 mb-3">{children}</h3>
  );
}

function Muted({ children }: { children: React.ReactNode }) {
  return <p style={{ color: "var(--color-muted)" }}>{children}</p>;
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <code
      className="text-sm px-1.5 py-0.5 rounded"
      style={{ background: "rgba(124,92,255,0.12)", color: "var(--color-accent)" }}
    >
      {children}
    </code>
  );
}

function Pre({ children }: { children: string }) {
  return (
    <pre
      className="mt-4 p-5 rounded-xl text-sm overflow-auto"
      style={{
        background: "var(--color-bg-surface)",
        border: "1px solid rgba(255,255,255,0.08)",
        color: "#d4d4d8",
        lineHeight: 1.65,
      }}
    >
      {children}
    </pre>
  );
}

function Table({
  headers,
  rows,
}: {
  headers: string[];
  rows: string[][];
}) {
  return (
    <div className="overflow-x-auto mt-6 rounded-xl" style={{ border: "1px solid rgba(255,255,255,0.08)" }}>
      <table className="w-full text-sm">
        <thead>
          <tr>
            {headers.map((h) => (
              <th
                key={h}
                className="text-left p-4"
                style={{ background: "var(--color-bg-surface)", color: "var(--color-muted)", fontWeight: 600 }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
              {row.map((cell, ci) => (
                <td
                  key={ci}
                  className="p-4"
                  style={{ color: ci === 0 ? "var(--color-text)" : "var(--color-muted)" }}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Callout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="mt-6 p-5 rounded-xl text-sm"
      style={{
        borderLeft: "3px solid var(--color-accent)",
        background: "rgba(124,92,255,0.07)",
        color: "var(--color-text)",
      }}
    >
      {children}
    </div>
  );
}

/* ── pipeline step ── */
function PipeStep({
  title,
  desc,
  last,
  accent,
}: {
  title: string;
  desc: React.ReactNode;
  last?: boolean;
  accent?: boolean;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className="w-3 h-3 rounded-full mt-1"
          style={{ background: accent ? "var(--color-accent-2)" : "var(--color-accent)" }}
        />
        {!last && (
          <div
            className="w-px flex-1 mt-1 min-h-8"
            style={{ background: "rgba(255,255,255,0.1)" }}
          />
        )}
      </div>
      <div className="pb-8 flex-1">
        <p className="font-semibold text-sm mb-1">{title}</p>
        <div className="text-sm" style={{ color: "var(--color-muted)" }}>
          {desc}
        </div>
      </div>
    </div>
  );
}

/* ── preset card ── */
function PresetCard({ id, title, body }: { id: string; title: string; body: string }) {
  return (
    <div
      className="p-5 rounded-xl"
      style={{
        background: "var(--color-bg-surface)",
        border: "1px solid rgba(255,255,255,0.1)",
      }}
    >
      <div className="flex items-baseline gap-2 mb-2">
        <span className="text-2xl font-bold" style={{ color: "var(--color-accent)" }}>
          {id}
        </span>
        <span className="font-semibold">{title}</span>
      </div>
      <p className="text-sm" style={{ color: "var(--color-muted)" }}>
        {body}
      </p>
    </div>
  );
}

/* ── english content ── */
const en = {
  title: "Technical Blueprint",
  subtitle:
    "Document question-answering without a vector database. Two explicit LLM pipelines over plain Markdown indexes.",
  toc: [
    { href: "#what", label: "What is NoRag?" },
    { href: "#l1", label: "L1 Pipeline" },
    { href: "#multil", label: "Multi_L Pipeline" },
    { href: "#comparison", label: "NoRag vs RAG" },
    { href: "#cost", label: "Cost Analysis" },
    { href: "#usecases", label: "Use Cases" },
    { href: "#quickstart", label: "Quick Start" },
  ],
  sections: {
    what: {
      heading: "What is NoRag?",
      body: "NoRag is a document Q&A system with no embedding layer. Where classical RAG transforms documents into opaque mathematical vectors, NoRag keeps everything in plain, readable Markdown and delegates routing to the contextual intelligence of modern LLMs.",
      layout: "Index layout",
      layoutCode: `data/
├── index.md                ← document catalog (doc_id, sections, keywords)
├── index_system_prompt.md  ← agent catalog (agent_id, capabilities, system prompt)
└── documents/
    ├── contract_saas.md    ← full text, split by ## section_id headers
    └── ...`,
      note: "index.md is the routing brain — it lists every document with its sections and keywords, compact enough to fit in a single LLM context window.",
    },
    l1: {
      heading: "The L1 Pipeline — 2 calls, deterministic",
      intro: "L1 is the core NoRag primitive. Every request is resolved in exactly two LLM calls, no matter how complex the question.",
      steps: [
        {
          title: "Call 1 — Router (SLM)",
          desc: "Reads index.md + index_system_prompt.md + the user question. Returns structured JSON: { agent_id, documents: [{ doc_id, sections }], reasoning }. A small, fast model handles this cheaply.",
          accent: false,
        },
        {
          title: "Storage read",
          desc: "The engine extracts the selected ## section_id blocks from document files. No similarity search — pure regex on known section headers.",
          accent: false,
        },
        {
          title: "Call 2 — Answer (LLM)",
          desc: "Receives the agent system prompt + full extracted sections + the question. Responds with mandatory citations [doc_id, section_id]. A capable model handles this.",
          accent: false,
        },
        {
          title: "L1Result",
          desc: "{ answer, citations, agent_id, tokens: { router, answer } }. Every citation is traceable to an exact section in an exact document.",
          accent: true,
        },
      ],
      example: `POST /query
{
  "question": "What SLA is guaranteed in the SaaS contract?",
  "mode": "L1"
}

→ {
  "answer": "The SaaS contract guarantees 99.9% uptime ...",
  "citations": [{"doc_id": "contract_saas", "section": "sla_guarantees"}],
  "agent_id": "juriste_conformite",
  "tokens": {"router": 1820, "answer": 3410}
}`,
      callout:
        "The Router reads both index files in a single call, selecting both the right documents and the right agent simultaneously — keeping the total at exactly 2 LLM calls.",
    },
    multil: {
      heading: "The Multi_L Pipeline — parallel, then synthesized",
      intro:
        "Multi_L fans out N independent L1 layers, runs them concurrently, then synthesizes through an Aggregator LLM. Use it for multi-perspective analysis, question decomposition, or corpus partitioning.",
      steps: [
        {
          title: "Planner (SLM)",
          desc: "Reads index.md + question + preset → emits a JSON array of layer plans: [{ agent_id, index_scope, sub_question }]. Capped at multil_max_layers (default 3).",
          accent: false,
        },
        {
          title: "N × L1 in parallel",
          desc: "Each layer plan spawns a full L1 run (Router + Answer) with its own agent, scoped index, and sub-question. All layers run concurrently with asyncio.gather. Each has a configurable timeout.",
          accent: false,
        },
        {
          title: "Aggregator (LLM)",
          desc: "Receives all layer answers. Writes a unified synthesis that explicitly names contradictions, preserves all citations, and notes which layer produced which insight.",
          accent: true,
        },
      ],
      presetsHeading: "Four presets",
      presets: [
        { id: "A", title: "Multi-Agent", body: "Same question, different agents. Cross-perspective analysis in one response." },
        { id: "B", title: "Decomposition", body: "Split the question into independent sub-questions, each routed separately." },
        { id: "C", title: "Multi-Corpus", body: "Same question, different agents, different document scopes." },
        { id: "D", title: "Hybrid / Auto", body: "The Planner freely combines agents, sub-questions, and index scopes." },
      ],
    },
    comparison: {
      heading: "NoRag vs RAG — Technical Comparison",
      headers: ["Criterion", "RAG (classical)", "NoRag"],
      rows: [
        ["Routing method", "Cosine similarity on vectors", "LLM semantic routing on Markdown index"],
        ["Infrastructure", "Vector DB (Pinecone, Weaviate, pgvector…)", "Plain Markdown files"],
        ["Embeddings", "✗ Required (cost per token)", "✓ None"],
        ["Human readability", "✗ Opaque vectors", "✓ 100% — any text editor"],
        ["Context given to LLM", "Arbitrary top-K chunks", "Complete named sections"],
        ["Citations", "Approximate (chunk offset)", "✓ Exact [doc_id, section]"],
        ["Session memory", "Must be implemented separately", "✓ Native via index files"],
        ["Auditability", "Debug requires ML expertise", "✓ Read the index, see the routing"],
        ["Scalability", "✓ Billions of documents", "Up to ~500 documents"],
        ["Setup complexity", "2–6 weeks", "2–4 hours (or 5 min with no-code mode)"],
        ["Vendor lock-in", "High (Pinecone, Weaviate migration is costly)", "✓ None — plain .md files"],
      ],
    },
    cost: {
      heading: "Cost Analysis",
      setupHeading: "Setup costs",
      setupHeaders: ["Item", "NoRag", "RAG (classical)"],
      setupRows: [
        ["Infrastructure", "$0 local / ~$25/mo Supabase Pro", "$70–500/mo (Pinecone, Weaviate)"],
        ["Embedding API", "$0 — no embeddings", "$0.02–0.13 per 1M tokens"],
        ["Initial dev time", "2–4 hours", "2–6 weeks"],
        ["Required skills", "Basic Python (or zero — no-code mode)", "ML + DevOps + advanced Python"],
        ["Team onboarding", "< 1 day", "1–4 weeks"],
      ],
      perReqHeading: "Per-request cost comparison",
      perReqHeaders: ["Pipeline", "Tokens", "Est. cost"],
      perReqRows: [
        ["NoRag — Router call (index ~5K + question)", "~6K input", "$0.0009"],
        ["NoRag — Answer call (sections ~10K + question)", "~12K in + 1K out", "$0.0020"],
        ["NoRag total (Gemini Flash)", "~18K tokens", "~$0.003"],
        ["RAG — Embedding query", "~50 tokens", "$0.000001"],
        ["RAG — Vector search (Pinecone)", "—", "~$0.0001"],
        ["RAG — Top-5 chunks + answer (GPT-4o)", "~3K in + 500 out", "$0.0135"],
        ["RAG total (GPT-4o + Pinecone)", "~3K LLM tokens", "~$0.014"],
      ],
      tcoHeading: "12-month TCO — 1,000 req/month, 100 documents",
      tcoHeaders: ["Scenario", "NoRag (Gemini Flash)", "RAG (GPT-4o + Pinecone)"],
      tcoRows: [
        ["Setup", "~$2", "$500–2,000 (dev time)"],
        ["Infrastructure / year", "$0–300", "$840–6,000"],
        ["LLM requests / year", "$36", "$168"],
        ["Maintenance / year", "$60", "$500–1,500"],
        ["Total 12 months", "~$100–400", "~$2,000–10,000"],
      ],
      callout:
        "NoRag with Gemini Flash is 4–5× cheaper per request than a typical RAG pipeline on GPT-4o, despite consuming more tokens — because Gemini Flash is 10–20× cheaper per token.",
    },
    usecases: {
      heading: "When to Use NoRag",
      yesHeading: "Choose NoRag when:",
      yesHeaders: ["Use case", "Why NoRag"],
      yesRows: [
        ["Private library (10–500 docs)", "Readable index, instant setup, precise citations"],
        ["Internal knowledge base", "Full control, auditability, no vendor lock-in"],
        ["Prototype / MVP", "No-code mode operational in 5 minutes"],
        ["Critical technical docs", "Section-level citations, guaranteed traceability"],
        ["Non-technical team", "Markdown index editable in Notion or Excel"],
        ["Limited budget", "No Vector DB, no separate embedding API"],
        ["Cross-document questions", "LLM intelligently combines multiple documents"],
        ["Compliance / auditability", "Every routing decision is explainable"],
      ],
      noHeading: "Choose RAG when:",
      noHeaders: ["Use case", "Why RAG"],
      noRows: [
        ["Massive corpus (1,000+ docs)", "Vector search scales; LLM index becomes impractical"],
        ["Real-time updates", "New documents indexed in seconds"],
        ["Multimodal content", "Image/audio/video embeddings (CLIP, Whisper…)"],
        ["Experienced ML team", "Stack well understood, monitoring in place"],
        ["Consumer-scale app", "Scalability critical — millions of users"],
      ],
    },
    quickstart: {
      heading: "Quick Start",
      apiHeading: "Mode A — API (FastAPI)",
      apiCode: `git clone https://github.com/supergmax/NoRag
cd NoRag
pip install -e ".[dev]"
export GEMINI_API_KEY=your_key

uvicorn api.main:app --reload

# L1 query
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "What are the SLA terms?", "mode": "L1"}'

# Multi_L preset A
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "Analyze risk across all contracts", "mode": "MultiL", "preset": "A"}'`,
      skillHeading: "Mode B — Claude Code skill",
      skillCode: `/norag What are the SLA terms in the SaaS contract?
/norag multi_l A Analyze our contracts from all angles
/norag list
/norag agents`,
      structureHeading: "Project structure",
      structureCode: `NoRag/
├── core/
│   ├── config.py          ← ROUTER_MODEL, ANSWER_MODEL, AGGREGATOR_MODEL
│   ├── storage.py         ← read_index(), read_document_sections()
│   ├── llm_client.py      ← generate(), generate_json()
│   ├── l1_engine.py       ← L1Engine.run()
│   ├── multi_l_engine.py  ← MultiLEngine.run()
│   ├── indexer.py         ← Indexer.ingest()
│   └── prompts/
│       ├── router.md
│       ├── planner.md
│       └── aggregator.md
├── api/
│   ├── main.py            ← FastAPI app, create_app()
│   └── schemas.py         ← Pydantic v2 models
├── data/
│   ├── index.md
│   ├── index_system_prompt.md
│   └── documents/
└── tests/                 ← 28 tests, all green`,
    },
  },
};

/* ── french content ── */
const fr: typeof en = {
  title: "Blueprint Technique",
  subtitle:
    "Question-réponse documentaire sans base vectorielle. Deux pipelines LLM explicites sur des index Markdown simples.",
  toc: [
    { href: "#what", label: "Qu'est-ce que NoRag ?" },
    { href: "#l1", label: "Pipeline L1" },
    { href: "#multil", label: "Pipeline Multi_L" },
    { href: "#comparison", label: "NoRag vs RAG" },
    { href: "#cost", label: "Analyse des coûts" },
    { href: "#usecases", label: "Cas d'usage" },
    { href: "#quickstart", label: "Démarrage rapide" },
  ],
  sections: {
    what: {
      heading: "Qu'est-ce que NoRag ?",
      body: "NoRag est un système de question-réponse documentaire sans couche d'embedding. Là où le RAG classique transforme vos documents en vecteurs mathématiques opaques, NoRag conserve tout en Markdown lisible et délègue le routage à l'intelligence contextuelle des LLM modernes.",
      layout: "Structure des index",
      layoutCode: `data/
├── index.md                ← catalogue de documents (doc_id, sections, mots-clés)
├── index_system_prompt.md  ← catalogue d'agents (agent_id, capacités, system prompt)
└── documents/
    ├── contrat_saas.md     ← texte complet, découpé par headers ## section_id
    └── ...`,
      note: "index.md est le cerveau du routage — il liste chaque document avec ses sections et mots-clés, assez compact pour tenir dans une fenêtre de contexte LLM.",
    },
    l1: {
      heading: "Le Pipeline L1 — 2 appels, déterministe",
      intro: "L1 est la brique fondamentale de NoRag. Chaque requête est résolue en exactement deux appels LLM, quelle que soit la complexité de la question.",
      steps: [
        {
          title: "Appel 1 — Routeur (SLM)",
          desc: "Lit index.md + index_system_prompt.md + la question utilisateur. Retourne un JSON structuré : { agent_id, documents: [{ doc_id, sections }], reasoning }. Un petit modèle rapide gère cela à faible coût.",
          accent: false,
        },
        {
          title: "Lecture du stockage",
          desc: "Le moteur extrait les blocs ## section_id sélectionnés depuis les fichiers de documents. Pas de recherche par similarité — simple extraction regex sur des headers connus.",
          accent: false,
        },
        {
          title: "Appel 2 — Réponse (LLM)",
          desc: "Reçoit le system prompt de l'agent + les sections extraites complètes + la question. Répond avec des citations obligatoires [doc_id, section_id]. Un modèle capable gère cela.",
          accent: false,
        },
        {
          title: "L1Result",
          desc: "{ answer, citations, agent_id, tokens: { router, answer } }. Chaque citation est traçable jusqu'à une section précise d'un document précis.",
          accent: true,
        },
      ],
      example: `POST /query
{
  "question": "Quel SLA est garanti dans le contrat SaaS ?",
  "mode": "L1"
}

→ {
  "answer": "Le contrat SaaS garantit une disponibilité de 99,9% ...",
  "citations": [{"doc_id": "contrat_saas", "section": "sla_garanties"}],
  "agent_id": "juriste_conformite",
  "tokens": {"router": 1820, "answer": 3410}
}`,
      callout:
        "Le Routeur lit les deux fichiers d'index en un seul appel, sélectionnant à la fois les bons documents et le bon agent — gardant le total à exactement 2 appels LLM.",
    },
    multil: {
      heading: "Le Pipeline Multi_L — parallèle, puis synthétisé",
      intro:
        "Multi_L distribue N couches L1 indépendantes, les exécute en parallèle, puis synthétise via un LLM Agrégateur. Utilisez-le pour l'analyse multi-perspectives, la décomposition de questions ou le partitionnement de corpus.",
      steps: [
        {
          title: "Planificateur (SLM)",
          desc: "Lit index.md + question + preset → émet un tableau JSON de plans de couches : [{ agent_id, index_scope, sub_question }]. Limité à multil_max_layers (défaut 3).",
          accent: false,
        },
        {
          title: "N × L1 en parallèle",
          desc: "Chaque plan de couche lance un L1 complet (Routeur + Réponse) avec son propre agent, index scopé et sous-question. Toutes les couches s'exécutent en parallèle via asyncio.gather. Chacune a un timeout configurable.",
          accent: false,
        },
        {
          title: "Agrégateur (LLM)",
          desc: "Reçoit toutes les réponses des couches. Rédige une synthèse unifiée qui nomme explicitement les contradictions, préserve toutes les citations et indique quelle couche a produit quelle information.",
          accent: true,
        },
      ],
      presetsHeading: "Quatre presets",
      presets: [
        { id: "A", title: "Multi-Agent", body: "Même question, agents différents. Analyse croisée en une seule réponse." },
        { id: "B", title: "Décomposition", body: "Découpe la question en sous-questions indépendantes, chacune routée séparément." },
        { id: "C", title: "Multi-Corpus", body: "Même question, agents différents, corpus distincts." },
        { id: "D", title: "Hybride / Auto", body: "Le Planificateur combine librement agents, sous-questions et corpus." },
      ],
    },
    comparison: {
      heading: "NoRag vs RAG — Comparatif Technique",
      headers: ["Critère", "RAG (classique)", "NoRag"],
      rows: [
        ["Méthode de routage", "Similarité cosinus sur vecteurs", "Routage LLM sémantique sur index Markdown"],
        ["Infrastructure", "Vector DB (Pinecone, Weaviate, pgvector…)", "Fichiers Markdown simples"],
        ["Embeddings", "✗ Obligatoires (coût par token)", "✓ Aucun"],
        ["Lisibilité humaine", "✗ Vecteurs opaques", "✓ 100% — tout éditeur de texte"],
        ["Contexte fourni au LLM", "Chunks top-K arbitraires", "Sections nommées complètes"],
        ["Citations", "Approximatives (offset chunk)", "✓ Précises [doc_id, section]"],
        ["Mémoire de session", "À implémenter séparément", "✓ Native via fichiers index"],
        ["Auditabilité", "Debug nécessite expertise ML", "✓ Lisez l'index, voyez le routage"],
        ["Scalabilité", "✓ Milliards de documents", "Jusqu'à ~500 documents"],
        ["Complexité setup", "2–6 semaines", "2–4 heures (ou 5 min en mode no-code)"],
        ["Vendor lock-in", "Élevé (migration Pinecone, Weaviate coûteuse)", "✓ Aucun — fichiers .md simples"],
      ],
    },
    cost: {
      heading: "Analyse des Coûts",
      setupHeading: "Coûts de mise en place",
      setupHeaders: ["Poste", "NoRag", "RAG (classique)"],
      setupRows: [
        ["Infrastructure", "$0 local / ~$25/mois Supabase Pro", "$70–500/mois (Pinecone, Weaviate)"],
        ["API d'embedding", "$0 — aucun embedding", "$0.02–0.13 par 1M tokens"],
        ["Temps dev initial", "2–4 heures", "2–6 semaines"],
        ["Compétences requises", "Python basique (ou zéro — mode no-code)", "ML + DevOps + Python avancé"],
        ["Formation équipe", "< 1 journée", "1–4 semaines"],
      ],
      perReqHeading: "Comparatif coût par requête",
      perReqHeaders: ["Pipeline", "Tokens", "Coût estimé"],
      perReqRows: [
        ["NoRag — Appel Routeur (index ~5K + question)", "~6K input", "0,0009 $"],
        ["NoRag — Appel Réponse (sections ~10K + question)", "~12K in + 1K out", "0,0020 $"],
        ["NoRag total (Gemini Flash)", "~18K tokens", "~0,003 $"],
        ["RAG — Embedding de la question", "~50 tokens", "0,000001 $"],
        ["RAG — Vector search (Pinecone)", "—", "~0,0001 $"],
        ["RAG — Top-5 chunks + réponse (GPT-4o)", "~3K in + 500 out", "0,0135 $"],
        ["RAG total (GPT-4o + Pinecone)", "~3K tokens LLM", "~0,014 $"],
      ],
      tcoHeading: "TCO sur 12 mois — 1 000 req/mois, 100 documents",
      tcoHeaders: ["Scénario", "NoRag (Gemini Flash)", "RAG (GPT-4o + Pinecone)"],
      tcoRows: [
        ["Setup", "~$2", "$500–2 000 (temps dev)"],
        ["Infrastructure / an", "$0–300", "$840–6 000"],
        ["LLM requêtes / an", "$36", "$168"],
        ["Maintenance / an", "$60", "$500–1 500"],
        ["Total 12 mois", "~$100–400", "~$2 000–10 000"],
      ],
      callout:
        "NoRag avec Gemini Flash est 4–5× moins cher par requête qu'un pipeline RAG sur GPT-4o, malgré plus de tokens consommés — car Gemini Flash est 10–20× moins cher par token.",
    },
    usecases: {
      heading: "Quand utiliser NoRag",
      yesHeading: "Choisir NoRag quand :",
      yesHeaders: ["Cas d'usage", "Pourquoi NoRag"],
      yesRows: [
        ["Bibliothèque privée (10–500 docs)", "Index lisible, setup immédiat, citations précises"],
        ["Base de connaissances interne", "Contrôle total, auditabilité, pas de vendor lock-in"],
        ["Prototype / MVP", "Mode no-code opérationnel en 5 minutes"],
        ["Documents techniques critiques", "Citations niveau section, traçabilité garantie"],
        ["Équipe non-technique", "Index Markdown éditable dans Notion ou Excel"],
        ["Budget limité", "Pas de Vector DB, pas d'API d'embedding séparée"],
        ["Questions transversales multi-docs", "Le LLM combine intelligemment plusieurs documents"],
        ["Conformité / auditabilité", "Chaque décision de routage est explicable"],
      ],
      noHeading: "Choisir RAG quand :",
      noHeaders: ["Cas d'usage", "Pourquoi RAG"],
      noRows: [
        ["Corpus massif (1 000+ docs)", "Vector search scalable ; index LLM impraticable"],
        ["Mises à jour temps réel", "Nouveaux documents indexés en secondes"],
        ["Contenu multimodal", "Embeddings image/audio/vidéo (CLIP, Whisper…)"],
        ["Équipe ML expérimentée", "Stack maîtrisée, monitoring en place"],
        ["App grand public", "Scalabilité critique — millions d'utilisateurs"],
      ],
    },
    quickstart: {
      heading: "Démarrage Rapide",
      apiHeading: "Mode A — API (FastAPI)",
      apiCode: `git clone https://github.com/supergmax/NoRag
cd NoRag
pip install -e ".[dev]"
export GEMINI_API_KEY=votre_clé

uvicorn api.main:app --reload

# Requête L1
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "Quels sont les termes SLA ?", "mode": "L1"}'

# Multi_L preset A
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "Analysez les risques dans tous les contrats", "mode": "MultiL", "preset": "A"}'`,
      skillHeading: "Mode B — Skill Claude Code",
      skillCode: `/norag Quels sont les termes SLA du contrat SaaS ?
/norag multi_l A Analysez nos contrats sous tous les angles
/norag list
/norag agents`,
      structureHeading: "Structure du projet",
      structureCode: `NoRag/
├── core/
│   ├── config.py          ← ROUTER_MODEL, ANSWER_MODEL, AGGREGATOR_MODEL
│   ├── storage.py         ← read_index(), read_document_sections()
│   ├── llm_client.py      ← generate(), generate_json()
│   ├── l1_engine.py       ← L1Engine.run()
│   ├── multi_l_engine.py  ← MultiLEngine.run()
│   ├── indexer.py         ← Indexer.ingest()
│   └── prompts/
│       ├── router.md
│       ├── planner.md
│       └── aggregator.md
├── api/
│   ├── main.py            ← application FastAPI, create_app()
│   └── schemas.py         ← modèles Pydantic v2
├── data/
│   ├── index.md
│   ├── index_system_prompt.md
│   └── documents/
└── tests/                 ← 28 tests, tous verts`,
    },
  },
};

/* ── page ── */
export default function BlueprintPage() {
  const { lang } = useLang();
  const c = lang === "fr" ? fr : en;
  const s = c.sections;

  return (
    <div className="pt-16">
      {/* Hero */}
      <div
        className="py-20 px-6 text-center"
        style={{ borderBottom: "1px solid rgba(255,255,255,0.07)" }}
      >
        <p
          className="text-xs font-semibold tracking-widest uppercase mb-4"
          style={{ color: "var(--color-accent)" }}
        >
          NoRag v2
        </p>
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
          {c.title}
        </h1>
        <p className="text-lg max-w-2xl mx-auto" style={{ color: "var(--color-muted)" }}>
          {c.subtitle}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link
            href="/"
            className="px-5 py-2.5 rounded-full text-sm transition-colors hover:text-white"
            style={{ border: "1px solid rgba(255,255,255,0.15)", color: "var(--color-muted)" }}
          >
            ← {lang === "fr" ? "Retour au site" : "Back to site"}
          </Link>
          <a
            href="https://github.com/supergmax/NoRag"
            target="_blank"
            rel="noopener noreferrer"
            className="px-5 py-2.5 rounded-full text-sm font-medium hover:opacity-90 transition"
            style={{ background: "var(--color-accent)", color: "#fff" }}
          >
            GitHub
          </a>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-16 flex gap-12">
        {/* ToC sidebar (desktop) */}
        <nav className="hidden lg:block w-52 shrink-0">
          <div className="sticky top-24">
            <p
              className="text-xs font-semibold uppercase tracking-wider mb-4"
              style={{ color: "var(--color-muted)" }}
            >
              {lang === "fr" ? "Sommaire" : "Contents"}
            </p>
            <ul className="space-y-2">
              {c.toc.map((item) => (
                <li key={item.href}>
                  <a
                    href={item.href}
                    className="text-sm transition-colors hover:text-white block"
                    style={{ color: "var(--color-muted)" }}
                  >
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </nav>

        {/* Content */}
        <div className="flex-1 min-w-0">

          {/* 1 — What is NoRag */}
          <Section id="what">
            <H2>{s.what.heading}</H2>
            <Muted>{s.what.body}</Muted>
            <H3>{s.what.layout}</H3>
            <Pre>{s.what.layoutCode}</Pre>
            <Callout>{s.what.note}</Callout>
          </Section>

          {/* 2 — L1 */}
          <Section id="l1">
            <H2>{s.l1.heading}</H2>
            <Muted>{s.l1.intro}</Muted>
            <div className="mt-8">
              {s.l1.steps.map((step, i) => (
                <PipeStep
                  key={i}
                  title={step.title}
                  desc={step.desc}
                  last={i === s.l1.steps.length - 1}
                  accent={step.accent}
                />
              ))}
            </div>
            <Pre>{s.l1.example}</Pre>
            <Callout>{s.l1.callout}</Callout>
          </Section>

          {/* 3 — Multi_L */}
          <Section id="multil">
            <H2>{s.multil.heading}</H2>
            <Muted>{s.multil.intro}</Muted>
            <div className="mt-8">
              {s.multil.steps.map((step, i) => (
                <PipeStep
                  key={i}
                  title={step.title}
                  desc={step.desc}
                  last={i === s.multil.steps.length - 1}
                  accent={step.accent}
                />
              ))}
            </div>
            <H3>{s.multil.presetsHeading}</H3>
            <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {s.multil.presets.map((p) => (
                <PresetCard key={p.id} {...p} />
              ))}
            </div>
          </Section>

          {/* 4 — Comparison */}
          <Section id="comparison">
            <H2>{s.comparison.heading}</H2>
            <Table headers={s.comparison.headers} rows={s.comparison.rows} />
          </Section>

          {/* 5 — Cost */}
          <Section id="cost">
            <H2>{s.cost.heading}</H2>
            <H3>{s.cost.setupHeading}</H3>
            <Table headers={s.cost.setupHeaders} rows={s.cost.setupRows} />
            <H3>{s.cost.perReqHeading}</H3>
            <Table headers={s.cost.perReqHeaders} rows={s.cost.perReqRows} />
            <H3>{s.cost.tcoHeading}</H3>
            <Table headers={s.cost.tcoHeaders} rows={s.cost.tcoRows} />
            <Callout>{s.cost.callout}</Callout>
          </Section>

          {/* 6 — Use cases */}
          <Section id="usecases">
            <H2>{s.usecases.heading}</H2>
            <H3>{s.usecases.yesHeading}</H3>
            <Table headers={s.usecases.yesHeaders} rows={s.usecases.yesRows} />
            <H3>{s.usecases.noHeading}</H3>
            <Table headers={s.usecases.noHeaders} rows={s.usecases.noRows} />
          </Section>

          {/* 7 — Quick start */}
          <Section id="quickstart">
            <H2>{s.quickstart.heading}</H2>
            <H3>{s.quickstart.apiHeading}</H3>
            <Pre>{s.quickstart.apiCode}</Pre>
            <H3>{s.quickstart.skillHeading}</H3>
            <Pre>{s.quickstart.skillCode}</Pre>
            <H3>{s.quickstart.structureHeading}</H3>
            <Pre>{s.quickstart.structureCode}</Pre>
          </Section>

        </div>
      </div>

      {/* Footer */}
      <div
        className="py-10 px-6 text-center text-sm"
        style={{ borderTop: "1px solid rgba(255,255,255,0.07)", color: "var(--color-muted)" }}
      >
        NoRag v2 ·{" "}
        <a
          href="https://github.com/supergmax/NoRag"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-white transition-colors"
        >
          github.com/supergmax/NoRag
        </a>{" "}
        · 2026
      </div>
    </div>
  );
}
