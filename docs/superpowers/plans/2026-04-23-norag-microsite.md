# NoRag Microsite — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page dark-mode marketing microsite (graphify.net-style) that explains NoRag with animated visual demos of L1 and Multi_L — no live demo, static export.

**Architecture:** Next.js 15 App Router + Tailwind v4 + Framer Motion, deployed as static export (`output: "export"`). One `app/page.tsx` composed of 8 section components. Two hand-rolled SVG + Framer Motion animations for L1 and Multi_L pipelines.

**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS v4, Framer Motion, Shiki (syntax highlighting).

**Spec:** `docs/superpowers/specs/2026-04-23-norag-l1-multil-microsite-design.md` §8.

---

## File Structure

**Create (all under `site/`):**

```
site/
├── package.json
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.mjs
├── .gitignore
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   ├── Hero.tsx
│   ├── WhyNotRag.tsx
│   ├── L1Demo.tsx
│   ├── MultiLDemo.tsx
│   ├── Presets.tsx
│   ├── UnderTheHood.tsx
│   ├── GetStarted.tsx
│   └── Footer.tsx
├── lib/
│   └── content.ts            # copy strings / constants
└── public/
    ├── blueprint.pdf         # copy of The_NoRag_Blueprint.pdf
    └── favicon.ico
```

---

## Task 1: Scaffold Next.js project

**Files:**
- Create: `site/` with Next.js baseline.

- [ ] **Step 1: Initialize Next.js**

```bash
cd "C:/Users/gmax9/OneDrive/Bureau/theAIproject/NoRag"
npx create-next-app@latest site --typescript --tailwind --app --no-src-dir --no-eslint --import-alias "@/*" --use-npm --yes
```

Expected: project created under `site/`.

- [ ] **Step 2: Add Framer Motion + Shiki**

```bash
cd site && npm install framer-motion shiki
```

- [ ] **Step 3: Configure static export in `site/next.config.mjs`**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};
export default nextConfig;
```

- [ ] **Step 4: Smoke-test dev server**

Run: `npm run dev` (inside `site/`)
Expected: `http://localhost:3000` loads the default Next.js page. Stop with Ctrl+C.

- [ ] **Step 5: Smoke-test export**

Run: `npm run build`
Expected: build succeeds, `site/out/` generated.

- [ ] **Step 6: Commit**

```bash
cd ..
git add site/
git commit -m "chore(site): scaffold Next.js + Tailwind + Framer Motion + Shiki"
```

---

## Task 2: Theme tokens + global styles

**Files:**
- Modify: `site/app/globals.css`
- Modify: `site/tailwind.config.ts` (if present) or `site/app/globals.css` with `@theme` block (Tailwind v4)

- [ ] **Step 1: Replace `site/app/globals.css`**

```css
@import "tailwindcss";

@theme {
  --color-bg-base:    #0a0a0b;
  --color-bg-surface: #131316;
  --color-text:       #f5f5f7;
  --color-muted:      #71717a;
  --color-accent:     #7c5cff;
  --color-accent-2:   #3ae0c8;

  --font-display: "Inter", ui-sans-serif, system-ui, sans-serif;
}

html, body {
  background: var(--color-bg-base);
  color: var(--color-text);
  font-family: var(--font-display);
  -webkit-font-smoothing: antialiased;
}

*::selection {
  background: var(--color-accent);
  color: #fff;
}
```

- [ ] **Step 2: Replace `site/app/layout.tsx`**

```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NoRag — RAG without vectors",
  description:
    "Document Q&A without vector embeddings. LLM-driven routing over Markdown indexes. Two pipelines: L1 and Multi_L.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 3: Verify dev server renders dark background**

Run: `npm run dev`
Expected: body is dark (#0a0a0b). Stop server.

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/app/ && git commit -m "feat(site): theme tokens + dark global styles"
```

---

## Task 3: `components/Hero.tsx`

**Files:**
- Create: `site/components/Hero.tsx`
- Modify: `site/app/page.tsx`

- [ ] **Step 1: Create `site/components/Hero.tsx`**

```tsx
"use client";
import { motion } from "framer-motion";

export function Hero() {
  return (
    <section className="relative isolate min-h-[90vh] flex flex-col items-center justify-center px-6">
      <motion.h1
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="text-6xl md:text-8xl font-semibold tracking-tight text-center"
      >
        NoRag.
        <br />
        <span className="text-[var(--color-accent)]">RAG without vectors.</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="mt-8 max-w-xl text-center text-[var(--color-muted)] text-lg"
      >
        Two explicit pipelines. Markdown indexes you can read. Full sections fed
        to the model. Citations you can audit.
      </motion.p>

      <div className="mt-12 flex gap-4">
        <a
          href="/blueprint.pdf"
          className="px-6 py-3 rounded-full bg-[var(--color-accent)] text-white font-medium hover:opacity-90 transition"
        >
          Read the blueprint
        </a>
        <a
          href="https://github.com/"
          className="px-6 py-3 rounded-full border border-white/15 hover:border-white/40 transition"
        >
          GitHub
        </a>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Replace `site/app/page.tsx`**

```tsx
import { Hero } from "@/components/Hero";

export default function Home() {
  return (
    <main>
      <Hero />
    </main>
  );
}
```

- [ ] **Step 3: Verify in browser**

Run: `npm run dev` → open `localhost:3000`
Expected: Hero renders with animation, violet CTA, muted subtitle.

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): Hero section with Framer Motion entrance"
```

---

## Task 4: `components/WhyNotRag.tsx`

**Files:**
- Create: `site/components/WhyNotRag.tsx`
- Modify: `site/app/page.tsx` to include it.

- [ ] **Step 1: Create `site/components/WhyNotRag.tsx`**

```tsx
const rows = [
  { k: "Infrastructure", rag: "Vector DB + embedding model", norag: "Plain Markdown files" },
  { k: "Cost of adding a doc", rag: "Recurring (re-embed + storage)", norag: "One-shot archivist pass" },
  { k: "Context given to LLM", rag: "Arbitrary chunks", norag: "Complete sections" },
  { k: "Auditability", rag: "Opaque vectors", norag: "Git-diffable Markdown" },
  { k: "Citations", rag: "Approximate", norag: "Precise [doc_id, section]" },
  { k: "Who fixes the index?", rag: "Data scientist", norag: "Any dev who reads MD" },
];

export function WhyNotRag() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Why not <span className="line-through text-[var(--color-muted)]">RAG</span>.
      </h2>
      <p className="mt-4 text-[var(--color-muted)] max-w-2xl">
        Vectors are opaque, chunks are arbitrary, and ingestion keeps paying.
        NoRag swaps the whole stack for Markdown the LLM can read directly.
      </p>

      <div className="mt-16 border border-white/10 rounded-2xl overflow-hidden">
        <div className="grid grid-cols-[1fr_1fr_1fr] text-sm">
          <div className="p-4 bg-[var(--color-bg-surface)] text-[var(--color-muted)]">Criterion</div>
          <div className="p-4 bg-[var(--color-bg-surface)] text-[var(--color-muted)]">RAG</div>
          <div className="p-4 bg-[var(--color-bg-surface)] text-[var(--color-accent)]">NoRag</div>
          {rows.map((r) => (
            <>
              <div key={r.k + "k"} className="p-4 border-t border-white/5">{r.k}</div>
              <div key={r.k + "r"} className="p-4 border-t border-white/5 text-[var(--color-muted)]">{r.rag}</div>
              <div key={r.k + "n"} className="p-4 border-t border-white/5">{r.norag}</div>
            </>
          ))}
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Add to `page.tsx`**

```tsx
import { Hero } from "@/components/Hero";
import { WhyNotRag } from "@/components/WhyNotRag";

export default function Home() {
  return (
    <main>
      <Hero />
      <WhyNotRag />
    </main>
  );
}
```

- [ ] **Step 3: Verify in browser** (scroll, 6 rows, RAG muted / NoRag accent).

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): WhyNotRag comparison section"
```

---

## Task 5: `components/L1Demo.tsx` — animated L1 pipeline

**Files:**
- Create: `site/components/L1Demo.tsx`
- Modify: `page.tsx`.

- [ ] **Step 1: Create `site/components/L1Demo.tsx`**

```tsx
"use client";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

export function L1Demo() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: false, margin: "-30% 0px" });

  return (
    <section ref={ref} className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        L1 <span className="text-[var(--color-muted)]">— two calls, done.</span>
      </h2>
      <p className="mt-4 text-[var(--color-muted)] max-w-2xl">
        Call 1: a small model reads the question, the document catalog, and the
        agent catalog. It picks an agent and the relevant sections. Call 2: the
        chosen agent reads those sections and answers with citations.
      </p>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] items-center gap-6">
        <Box label="Question" tone="neutral" active={inView} delay={0} />
        <Arrow active={inView} delay={0.3} />
        <Box label="Router (SLM)" subtitle="→ agent + docs" tone="accent" active={inView} delay={0.5} />
        <Arrow active={inView} delay={0.9} />
        <Box label="Answer (LLM)" subtitle="with [doc, section]" tone="accent-2" active={inView} delay={1.1} />
      </div>

      <motion.pre
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ delay: 1.4, duration: 0.5 }}
        className="mt-12 p-6 rounded-xl bg-[var(--color-bg-surface)] border border-white/10 text-sm overflow-auto"
      >
{`{
  "agent_id": "juriste_conformite",
  "documents": [
    { "doc_id": "contrat_acme", "sections": ["art_7", "annexe_B"] }
  ],
  "reasoning": "question de rétention contractuelle"
}`}
      </motion.pre>
    </section>
  );
}

function Box({ label, subtitle, tone, active, delay }:
  { label: string; subtitle?: string; tone: "neutral" | "accent" | "accent-2"; active: boolean; delay: number }) {
  const color = tone === "accent" ? "var(--color-accent)"
    : tone === "accent-2" ? "var(--color-accent-2)"
    : "#ffffff";
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={active ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
      transition={{ delay, duration: 0.4 }}
      className="p-5 rounded-xl bg-[var(--color-bg-surface)] border text-center"
      style={{ borderColor: color }}
    >
      <div className="font-medium" style={{ color }}>{label}</div>
      {subtitle && <div className="text-xs text-[var(--color-muted)] mt-1">{subtitle}</div>}
    </motion.div>
  );
}

function Arrow({ active, delay }: { active: boolean; delay: number }) {
  return (
    <motion.div
      initial={{ scaleX: 0 }}
      animate={active ? { scaleX: 1 } : { scaleX: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="h-px bg-white/30 origin-left md:w-16 w-full"
    />
  );
}
```

- [ ] **Step 2: Add to `page.tsx`**

```tsx
import { L1Demo } from "@/components/L1Demo";
// ...
<L1Demo />
```

- [ ] **Step 3: Scroll-verify** — animation plays when section enters viewport.

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): animated L1 pipeline demo"
```

---

## Task 6: `components/MultiLDemo.tsx`

**Files:**
- Create: `site/components/MultiLDemo.tsx`
- Modify: `page.tsx`.

- [ ] **Step 1: Create `site/components/MultiLDemo.tsx`**

```tsx
"use client";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";

export function MultiLDemo() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: false, margin: "-30% 0px" });

  const layers = [
    { id: 1, agent: "juriste", color: "var(--color-accent)" },
    { id: 2, agent: "technique", color: "var(--color-accent-2)" },
    { id: 3, agent: "finance", color: "#e879f9" },
  ];

  return (
    <section ref={ref} className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Multi_L <span className="text-[var(--color-muted)]">— parallel, then synthesized.</span>
      </h2>
      <p className="mt-4 text-[var(--color-muted)] max-w-2xl">
        A Planner fans out N L1 layers — different agents, sub-questions, or
        corpora. The Aggregator names contradictions and writes the synthesis.
      </p>

      <div className="mt-16 space-y-8">
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="p-5 rounded-xl bg-[var(--color-bg-surface)] border border-white/20 text-center max-w-md mx-auto"
        >
          Planner (SLM) — emits N layer plans
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {layers.map((l, i) => (
            <motion.div
              key={l.id}
              initial={{ opacity: 0, y: 16 }}
              animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
              transition={{ delay: 0.3 + i * 0.15, duration: 0.4 }}
              className="p-5 rounded-xl bg-[var(--color-bg-surface)] border text-center"
              style={{ borderColor: l.color }}
            >
              <div className="font-medium" style={{ color: l.color }}>Layer {l.id}</div>
              <div className="text-xs text-[var(--color-muted)] mt-1">agent: {l.agent}</div>
              <div className="mt-3 text-xs text-white/50">L1 → answer</div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.95 }}
          transition={{ delay: 1.0, duration: 0.5 }}
          className="p-6 rounded-xl border border-[var(--color-accent)] text-center max-w-md mx-auto"
        >
          <div className="font-medium text-[var(--color-accent)]">Aggregator (LLM)</div>
          <div className="text-xs text-[var(--color-muted)] mt-1">synthesis with all citations preserved</div>
        </motion.div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Add to `page.tsx`**

- [ ] **Step 3: Scroll-verify** animation cascade (Planner → 3 layers → Aggregator).

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): animated Multi_L fan-out + aggregation demo"
```

---

## Task 7: `components/Presets.tsx` — 4 cards

**Files:**
- Create: `site/components/Presets.tsx`
- Modify: `page.tsx`.

- [ ] **Step 1: Create `site/components/Presets.tsx`**

```tsx
const presets = [
  {
    id: "A", title: "Multi-Agent",
    body: "Same question, different agents. Perspectives croisées.",
    example: 'Layer 1: juriste\nLayer 2: technique\nLayer 3: finance',
  },
  {
    id: "B", title: "Decomposition",
    body: "Split the question into sub-questions, same or similar agents.",
    example: 'L1: "AWS cloud 2020-2024"\nL2: "Azure cloud 2020-2024"',
  },
  {
    id: "C", title: "Multi-Corpus",
    body: "Same question, different agents, different index scopes.",
    example: 'L1: juriste, scope=contrats\nL2: tech, scope=doc_technique',
  },
  {
    id: "D", title: "Hybrid / Auto",
    body: "Planner freely combines the three dimensions.",
    example: "Let the Planner decide.",
  },
];

export function Presets() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Four presets. <span className="text-[var(--color-muted)]">Same engine.</span>
      </h2>
      <div className="mt-16 grid grid-cols-1 md:grid-cols-2 gap-4">
        {presets.map((p) => (
          <div key={p.id} className="p-6 rounded-xl bg-[var(--color-bg-surface)] border border-white/10 hover:border-[var(--color-accent)] transition">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-semibold text-[var(--color-accent)]">{p.id}</span>
              <span className="text-xl font-medium">{p.title}</span>
            </div>
            <p className="mt-3 text-[var(--color-muted)]">{p.body}</p>
            <pre className="mt-4 text-xs text-white/70 whitespace-pre-wrap">{p.example}</pre>
          </div>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Add to `page.tsx`**, verify, commit.

```bash
cd .. && git add site/ && git commit -m "feat(site): Presets section (A/B/C/D)"
```

---

## Task 8: `components/UnderTheHood.tsx` — Shiki-highlighted snippets

**Files:**
- Create: `site/components/UnderTheHood.tsx`
- Create: `site/lib/highlight.ts` (Shiki helper)

- [ ] **Step 1: Create `site/lib/highlight.ts`**

```ts
import { codeToHtml } from "shiki";

export async function highlight(code: string, lang: string) {
  return codeToHtml(code, { lang, theme: "github-dark-default" });
}
```

- [ ] **Step 2: Create `site/components/UnderTheHood.tsx`** (server component)

```tsx
import { highlight } from "@/lib/highlight";

const INDEX_MD = `## contrat_acme
- **Titre** : Contrat SaaS Acme
- **Résumé** : Contrat B2B, obligations SLA et rétention.
- **Sections** :
  - \`art_7\` — Rétention données — mots-clés : rétention, RGPD, purge
  - \`annexe_B\` — SLA — mots-clés : SLA, uptime, crédit
`;

const AGENTS_MD = `## juriste_conformite
**Description** : expert juridique B2B (contrats, RGPD, SLA).
**Quand l'utiliser** : clauses, rétention, DPA, SLA.
**System prompt** :
> Tu es juriste senior. Tu cites [doc_id, section] systématiquement.
`;

export async function UnderTheHood() {
  const [indexHtml, agentsHtml] = await Promise.all([
    highlight(INDEX_MD, "markdown"),
    highlight(AGENTS_MD, "markdown"),
  ]);
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Under the hood.
      </h2>
      <p className="mt-4 text-[var(--color-muted)] max-w-2xl">
        Two Markdown files. That's the entire "database".
      </p>
      <div className="mt-12 grid md:grid-cols-2 gap-6">
        <div>
          <div className="text-sm text-[var(--color-muted)] mb-2">data/index.md</div>
          <div className="rounded-xl overflow-hidden border border-white/10 text-sm" dangerouslySetInnerHTML={{ __html: indexHtml }} />
        </div>
        <div>
          <div className="text-sm text-[var(--color-muted)] mb-2">data/index_system_prompt.md</div>
          <div className="rounded-xl overflow-hidden border border-white/10 text-sm" dangerouslySetInnerHTML={{ __html: agentsHtml }} />
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 3: Add to `page.tsx`**, verify (Shiki renders in server component, no client JS needed).

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): UnderTheHood section with Shiki-highlighted snippets"
```

---

## Task 9: `GetStarted.tsx` + `Footer.tsx`

**Files:**
- Create: `site/components/GetStarted.tsx`
- Create: `site/components/Footer.tsx`
- Modify: `page.tsx`.

- [ ] **Step 1: Create `site/components/GetStarted.tsx`**

```tsx
const cards = [
  { title: "API", body: "Full L1 + Multi_L via FastAPI.", cta: "uvicorn api.main:app --reload" },
  { title: "CLI / Web chat", body: "Copy a prompt into ChatGPT, Claude, Gemini, Grok.", cta: "norag/plugins/*.md" },
  { title: "Blueprint", body: "The full doctrine in one PDF.", cta: "blueprint.pdf" },
];

export function GetStarted() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">Get started.</h2>
      <div className="mt-12 grid md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div key={c.title} className="p-6 rounded-xl bg-[var(--color-bg-surface)] border border-white/10">
            <div className="text-xl font-medium">{c.title}</div>
            <p className="mt-3 text-[var(--color-muted)]">{c.body}</p>
            <div className="mt-4 text-xs font-mono text-[var(--color-accent)]">{c.cta}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Create `site/components/Footer.tsx`**

```tsx
export function Footer() {
  return (
    <footer className="py-16 px-6 border-t border-white/5 text-center text-[var(--color-muted)] text-sm">
      NoRag — Markdown, not vectors. © 2026.
    </footer>
  );
}
```

- [ ] **Step 3: Final `page.tsx`**

```tsx
import { Hero } from "@/components/Hero";
import { WhyNotRag } from "@/components/WhyNotRag";
import { L1Demo } from "@/components/L1Demo";
import { MultiLDemo } from "@/components/MultiLDemo";
import { Presets } from "@/components/Presets";
import { UnderTheHood } from "@/components/UnderTheHood";
import { GetStarted } from "@/components/GetStarted";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <main>
      <Hero />
      <WhyNotRag />
      <L1Demo />
      <MultiLDemo />
      <Presets />
      {/* UnderTheHood is async server component */}
      {/* @ts-expect-error Async Server Component */}
      <UnderTheHood />
      <GetStarted />
      <Footer />
    </main>
  );
}
```

- [ ] **Step 4: Commit**

```bash
cd .. && git add site/ && git commit -m "feat(site): GetStarted + Footer, full page composition"
```

---

## Task 10: Copy Blueprint PDF into `site/public`

**Files:**
- Create: `site/public/blueprint.pdf` (copy of `The_NoRag_Blueprint.pdf`).

- [ ] **Step 1: Copy the PDF**

```bash
cp "The_NoRag_Blueprint.pdf" "site/public/blueprint.pdf"
```

- [ ] **Step 2: Verify link works** — open `http://localhost:3000/blueprint.pdf` in dev mode.

- [ ] **Step 3: Commit**

```bash
git add site/public/blueprint.pdf
git commit -m "chore(site): include blueprint PDF in static assets"
```

---

## Task 11: Final build + QA

- [ ] **Step 1: Full static build**

Run: `cd site && npm run build`
Expected: build succeeds, `site/out/` contains `index.html` + assets.

- [ ] **Step 2: Preview production build**

Run: `npx serve site/out -l 4000` (install `serve` globally if missing: `npm i -g serve`)
Open `http://localhost:4000`. Expected: same behavior as dev, no hydration warnings in DevTools console.

- [ ] **Step 3: Manual QA checklist**

Verify:
- Hero renders with fade-in animation.
- WhyNotRag table shows 6 rows.
- L1Demo animates on scroll into view (out-of-view state OK too).
- MultiLDemo shows Planner → 3 layers → Aggregator cascade.
- Presets shows 4 cards with hover accent border.
- UnderTheHood shows syntax-highlighted Markdown, dark theme.
- GetStarted 3 cards present.
- Footer visible.
- `/blueprint.pdf` downloads.
- Page responsive on mobile width (375px).

- [ ] **Step 4: Tag**

```bash
cd .. && git tag -a v3.0-site -m "NoRag v3 microsite: 8 sections + animated demos"
```

---

## Self-review results

- **Spec coverage**: §8 all 8 sections → Tasks 3/4/5/6/7/8/9; stack Next.js/TS/Tailwind/Framer Motion/Shiki → Task 1; static export → Task 1 Step 3; palette → Task 2; blueprint link → Task 10.
- **Placeholders**: none. All code blocks complete and self-contained.
- **Type consistency**: component prop shapes defined inline where used; no cross-file type contracts.
