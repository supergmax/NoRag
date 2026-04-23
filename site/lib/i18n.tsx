"use client";
import React, { createContext, useContext, useState } from "react";

export type Lang = "en" | "fr";

export const translations = {
  en: {
    header: {
      nav: [
        { label: "L1", href: "#l1" },
        { label: "Multi_L", href: "#multil" },
        { label: "Comparison", href: "#comparison" },
        { label: "Get started", href: "#get-started" },
      ],
    },
    hero: {
      subtitle:
        "Two explicit pipelines. Markdown indexes you can read. Full sections fed to the model. Citations you can audit.",
      cta1: "Read the blueprint",
      cta2: "GitHub",
    },
    whyNotRag: {
      title: "Why not",
      subtitle:
        "Vectors are opaque, chunks are arbitrary, and ingestion keeps paying. NoRag swaps the whole stack for Markdown the LLM can read directly.",
      headers: ["Criterion", "RAG", "NoRag"],
      rows: [
        { k: "Infrastructure",        rag: "Vector DB + embedding model",       norag: "Plain Markdown files" },
        { k: "Cost of adding a doc",  rag: "Recurring (re-embed + storage)",    norag: "One-shot archivist pass" },
        { k: "Context given to LLM",  rag: "Arbitrary chunks",                  norag: "Complete sections" },
        { k: "Auditability",          rag: "Opaque vectors",                    norag: "Git-diffable Markdown" },
        { k: "Citations",             rag: "Approximate",                       norag: "Precise [doc_id, section]" },
        { k: "Who fixes the index?",  rag: "Data scientist",                    norag: "Any dev who reads MD" },
      ],
    },
    l1Demo: {
      title: "L1",
      titleSub: "— two calls, done.",
      subtitle:
        "Call 1: a small model reads the question, the document catalog, and the agent catalog. It picks an agent and the relevant sections. Call 2: the chosen agent reads those sections and answers with citations.",
    },
    multiLDemo: {
      title: "Multi_L",
      titleSub: "— parallel, then synthesized.",
      subtitle:
        "A Planner fans out N L1 layers — different agents, sub-questions, or corpora. The Aggregator names contradictions and writes the synthesis.",
      plannerLabel: "Planner (SLM)",
      plannerSub: "emits N layer plans",
      layerSub: "L1 → answer + citations",
      aggregatorLabel: "Aggregator (LLM)",
      aggregatorSub: "synthesis · all citations preserved · contradictions named",
    },
    presets: {
      title: "Four presets.",
      titleSub: "Same engine.",
      subtitle:
        "Configure Multi_L for your use case by picking a preset — or let the Planner decide automatically.",
      items: [
        {
          title: "Multi-Agent",
          body: "Same question, different agents. Cross-perspectives in one response.",
          example: "Layer 1: juriste_conformite\nLayer 2: analyste_technique\nLayer 3: analyste_finance",
        },
        {
          title: "Decomposition",
          body: "Split the question into sub-questions routed independently.",
          example: 'L1: "AWS cloud strategy 2020-2024"\nL2: "Azure cloud strategy 2020-2024"',
        },
        {
          title: "Multi-Corpus",
          body: "Same question, different agents, different document scopes.",
          example: "L1: juriste, scope=contrats\nL2: analyste_technique, scope=doc_technique",
        },
        {
          title: "Hybrid / Auto",
          body: "Planner freely combines agents, sub-questions, and index scopes.",
          example: "Let the Planner decide.",
        },
      ],
    },
    underTheHood: {
      title: "Under the hood.",
      subtitle:
        "Two Markdown files. That’s the entire “database”. Git-diffable, human-readable, zero infra.",
    },
    getStarted: {
      title: "Get started.",
      cards: [
        {
          title: "API",
          body: "Full L1 + Multi_L via FastAPI. Any client, any language.",
          cta: "uvicorn api.main:app --reload",
        },
        {
          title: "Web chat",
          body: "Copy a plugin prompt into ChatGPT, Claude, Gemini, or Grok. L1 only.",
          cta: "norag/plugins/<provider>.md",
        },
        {
          title: "Claude Code skill",
          body: "Use /norag directly in your terminal. L1 + Multi_L, reads local files.",
          cta: "/norag <question>",
        },
      ],
    },
    footer: "NoRag — Markdown, not vectors. © 2026.",
  },

  fr: {
    header: {
      nav: [
        { label: "L1", href: "#l1" },
        { label: "Multi_L", href: "#multil" },
        { label: "Comparatif", href: "#comparison" },
        { label: "Commencer", href: "#get-started" },
      ],
    },
    hero: {
      subtitle:
        "Deux pipelines explicites. Des index Markdown lisibles. Des sections complètes transmises au modèle. Des citations auditables.",
      cta1: "Lire le blueprint",
      cta2: "GitHub",
    },
    whyNotRag: {
      title: "Pourquoi pas le",
      subtitle:
        "Les vecteurs sont opaques, les chunks arbitraires, et l’ingestion coûte en continu. NoRag remplace toute la stack par du Markdown que le LLM lit directement.",
      headers: ["Critère", "RAG", "NoRag"],
      rows: [
        { k: "Infrastructure",           rag: "Vector DB + modèle d’embedding",   norag: "Fichiers Markdown simples" },
        { k: "Ajout d’un document", rag: "Coût récurrent (re-embed + stockage)", norag: "Un seul passage Archiviste" },
        { k: "Contexte fourni au LLM",   rag: "Chunks arbitraires",                        norag: "Sections complètes" },
        { k: "Auditabilité",        rag: "Vecteurs opaques",                           norag: "Markdown versionné avec Git" },
        { k: "Citations",                rag: "Approximatives",                             norag: "Précises [doc_id, section]" },
        { k: "Qui corrige l’index ?", rag: "Data scientist",                           norag: "Tout dév qui lit le MD" },
      ],
    },
    l1Demo: {
      title: "L1",
      titleSub: "— deux appels, c’est tout.",
      subtitle:
        "Appel 1 : un petit modèle lit la question, le catalogue de documents et le catalogue d’agents. Il choisit un agent et les sections pertinentes. Appel 2 : l’agent sélectionné lit ces sections et répond avec des citations.",
    },
    multiLDemo: {
      title: "Multi_L",
      titleSub: "— parallèle, puis synthétisé.",
      subtitle:
        "Un Planificateur distribue N couches L1 — agents différents, sous-questions ou corpus distincts. L’Agrégateur nomme les contradictions et rédige la synthèse.",
      plannerLabel: "Planificateur (SLM)",
      plannerSub: "émet N plans de couches",
      layerSub: "L1 → réponse + citations",
      aggregatorLabel: "Agrégateur (LLM)",
      aggregatorSub: "synthèse · citations préservées · contradictions nommées",
    },
    presets: {
      title: "Quatre presets.",
      titleSub: "Même moteur.",
      subtitle:
        "Configurez Multi_L pour votre cas d’usage en choisissant un preset — ou laissez le Planificateur décider.",
      items: [
        {
          title: "Multi-Agent",
          body: "Même question, agents différents. Perspectives croisées en une seule réponse.",
          example: "Couche 1: juriste_conformite\nCouche 2: analyste_technique\nCouche 3: analyste_finance",
        },
        {
          title: "Décomposition",
          body: "Découpe la question en sous-questions routées indépendamment.",
          example: 'L1 : « Stratégie cloud AWS 2020-2024 »\nL2 : « Stratégie cloud Azure 2020-2024 »',
        },
        {
          title: "Multi-Corpus",
          body: "Même question, agents différents, corpus distincts.",
          example: "L1 : juriste, scope=contrats\nL2 : analyste_technique, scope=doc_technique",
        },
        {
          title: "Hybride / Auto",
          body: "Le Planificateur combine librement agents, sous-questions et corpus.",
          example: "Laisser le Planificateur décider.",
        },
      ],
    },
    underTheHood: {
      title: "Sous le capot.",
      subtitle:
        "Deux fichiers Markdown. C’est toute la « base de données ». Versionnable avec Git, lisible par tous, zéro infra.",
    },
    getStarted: {
      title: "Commencer.",
      cards: [
        {
          title: "API",
          body: "L1 + Multi_L complets via FastAPI. Tout client, tout langage.",
          cta: "uvicorn api.main:app --reload",
        },
        {
          title: "Chat web",
          body: "Copiez un prompt plugin dans ChatGPT, Claude, Gemini ou Grok. L1 uniquement.",
          cta: "norag/plugins/<provider>.md",
        },
        {
          title: "Skill Claude Code",
          body: "Utilisez /norag directement dans votre terminal. L1 + Multi_L, lit les fichiers locaux.",
          cta: "/norag <question>",
        },
      ],
    },
    footer: "NoRag — Markdown, pas des vecteurs. © 2026.",
  },
} as const;

export type Translations = (typeof translations)["en"];

interface LangContextType {
  lang: Lang;
  t: Translations;
  setLang: (l: Lang) => void;
}

const LangContext = createContext<LangContextType>({
  lang: "en",
  t: translations.en,
  setLang: () => {},
});

export function LangProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");
  return (
    <LangContext.Provider value={{ lang, t: translations[lang] as Translations, setLang }}>
      {children}
    </LangContext.Provider>
  );
}

export function useLang() {
  return useContext(LangContext);
}
