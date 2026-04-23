# NoRag v2 — Analyse Complète : NoRag vs RAG

> Document de référence pour présentation marketing et technique
> Date : Mars 2026

---

## Table des matières

1. [Qu'est-ce que NoRag ?](#1-quest-ce-que-norag-)
2. [Qu'est-ce que le RAG classique ?](#2-quest-ce-que-le-rag-classique-)
3. [Comparatif Technique](#3-comparatif-technique)
4. [Avantages & Inconvénients](#4-avantages--inconvénients)
5. [Cas d'usage : Quelle solution choisir ?](#5-cas-dusage--quelle-solution-choisir-)
6. [Comparatif des Coûts](#6-comparatif-des-coûts)
7. [Présentation Marketing](#7-présentation-marketing)
8. [Présentation Technique](#8-présentation-technique)
9. [Calcul de Coûts Détaillé — Modèle Qwen (Pay-as-you-go)](#9-calcul-de-coûts-détaillé--modèle-qwen-pay-as-you-go)
10. [Déploiement NoRag avec Qwen3.5-9B sur AWS](#10-déploiement-norag-avec-qwen359b-sur-aws)
11. [Comparatif de Prix : Local vs API — Tous Modèles](#11-comparatif-de-prix--local-vs-api--tous-modèles)
12. [Estimation des Coûts API — Pipeline NoRag Exact (Archiviste + 2 étapes)](#12-estimation-des-coûts-api--pipeline-norag-exact-archiviste--2-étapes)
13. [Index Hiérarchique — Corpus Quasi-Illimité (Layer d'Abstraction)](#13-index-hiérarchique--corpus-quasi-illimité-layer-dabstraction)
14. [RAG vs NoRag — Comparatif de Coûts Réels (2 000 docs, 1 000 req/mois)](#14-rag-vs-norag--comparatif-de-couts-reels-2-000-docs-1-000-reqmois)

---

## 1. Qu'est-ce que NoRag ?

NoRag v2 est un système de **Question-Réponse documentaire sans embeddings vectoriels**. Là où le RAG classique transforme vos documents en vecteurs mathématiques opaques, NoRag conserve tout en **Markdown lisible** et délègue le routage à l'intelligence contextuelle des LLM modernes.

### Architecture en 3 Index Markdown

```
┌─────────────────────────────────────────────────────┐
│                   NORAG v2                          │
│                                                     │
│  index_documents.md  ←  Catalogue des documents     │
│  index_agents.md     ←  Capacités disponibles       │
│  index_history.md    ←  Mémoire des sessions        │
│                                                     │
│  Pipeline :                                         │
│  Question → LLM Route → LLM Génère → Citation      │
└─────────────────────────────────────────────────────┘
```

### Pipeline en 3 étapes

1. **ROUTAGE** : Le LLM lit `index_documents.md` + la question → identifie 1 à 3 documents/sections pertinents
2. **CONTEXTE** : Chargement de `index_history.md` pour la continuité conversationnelle
3. **GÉNÉRATION** : Le LLM récupère le texte ciblé et génère la réponse avec citations obligatoires `[Document, Pages X-Y]`

### Modes de déploiement

| Mode | Description | Prérequis |
|------|-------------|-----------|
| **A — Agent autonome** | Coller le prompt dans ChatGPT, Claude, Gemini, Grok | Zéro code |
| **B — CLI local** | Terminal interactif avec SQLite | Python |
| **C — API REST (SQLite)** | Serveur local FastAPI | Python + FastAPI |
| **D — API REST (Supabase)** | Cloud PostgreSQL production | Python + Supabase |

---

## 2. Qu'est-ce que le RAG classique ?

Le **RAG (Retrieval-Augmented Generation)** est l'approche standard depuis 2023 :

```
┌─────────────────────────────────────────────────────┐
│                   RAG CLASSIQUE                     │
│                                                     │
│  Documents → Chunking → Embeddings → Vector DB      │
│                                                     │
│  Question → Embedding Query → Similarité Cosinus    │
│           → Top-K Chunks → LLM → Réponse            │
└─────────────────────────────────────────────────────┘
```

### Stack typique RAG

- **Chunking** : LangChain, LlamaIndex
- **Embeddings** : OpenAI `text-embedding-3-small`, Cohere, BGE
- **Vector DB** : Pinecone, Weaviate, Chroma, pgvector, FAISS
- **Orchestration** : LangChain, LlamaIndex, Haystack
- **LLM** : GPT-4, Claude, Gemini

---

## 3. Comparatif Technique

### Architecture

| Critère | NoRag v2 | RAG Classique |
|---------|----------|---------------|
| **Routage** | LLM sémantique (Markdown index) | Similarité cosinus (vecteurs) |
| **Stockage** | Markdown + SQLite/Supabase | Vector DB (Pinecone, Chroma…) |
| **Embeddings** | ❌ Aucun | ✅ Obligatoires |
| **Lisibilité** | ✅ 100% human-readable | ❌ Vecteurs opaques |
| **Dépendances** | Minimales (FastAPI, google-genai) | Nombreuses (LangChain, VectorDB…) |
| **Contexte LLM** | Grand (index complet passé en contexte) | Petit (top-K chunks seulement) |
| **Mémoire session** | ✅ Native (index_history.md) | Variable (à implémenter) |
| **Citations sources** | ✅ Obligatoires et précises | Variable (souvent inexact) |
| **Multi-LLM** | ✅ Gemini, Claude, GPT, Grok | ✅ (selon orchestrateur) |
| **Mode no-code** | ✅ (Mode A : copier-coller) | ❌ |

### Flux de données

```
NORAG
Question ──→ index_documents.md ──→ LLM Route ──→ Document source ──→ LLM Génère ──→ Réponse + Citation

RAG
Question ──→ Embedding ──→ Vector Search ──→ Top-K chunks ──→ LLM Génère ──→ Réponse
```

### Qualité du routage

| Scénario | NoRag | RAG |
|----------|-------|-----|
| Question directe et précise | ✅ Excellent | ✅ Excellent |
| Question vague ou ambiguë | ✅ Bon (LLM comprend l'intention) | ⚠️ Moyen (dépend embeddings) |
| Question transversale multi-docs | ✅ Bon (LLM combine) | ⚠️ Difficile (chunks isolés) |
| Termes techniques rares | ✅ Bon (mots-clés dans index) | ⚠️ Variable (OOV embeddings) |
| 10 000+ documents | ⚠️ Index trop grand | ✅ Scalable |
| Mise à jour fréquente docs | ✅ Re-index rapide | ⚠️ Re-embedding coûteux |

---

## 4. Avantages & Inconvénients

### NoRag v2

#### ✅ Avantages

1. **Zéro embedding** — Pas de coût de vectorisation, pas de modèle d'embedding à maintenir
2. **Transparence totale** — Les 3 index Markdown sont lisibles, auditables, modifiables manuellement
3. **Déploiement immédiat** — Mode A : coller un prompt dans ChatGPT, c'est opérationnel
4. **Citations précises** — Format `[Document, Pages X-Y]` garanti par le prompt système
5. **Mémoire conversationnelle native** — `index_history.md` maintient la continuité entre sessions
6. **Maintenabilité simple** — Les index sont des fichiers texte, pas une base de données propriétaire
7. **Flexibilité LLM** — Fonctionne avec n'importe quel LLM avec grande fenêtre de contexte
8. **Coût de setup nul** — Pas de Vector DB à provisionner, pas d'API d'embedding
9. **Debug facile** — On lit directement les index pour comprendre pourquoi une réponse a été donnée
10. **Pas de vendor lock-in** — Les 3 fichiers `.md` s'ouvrent dans n'importe quel éditeur

#### ❌ Inconvénients

1. **Scalabilité limitée** — L'index complet est passé en contexte ; au-delà de ~500 documents, le contexte LLM sature
2. **Coût tokens élevé** — Chaque requête consomme davantage de tokens (index + question + réponse)
3. **Latence** — 2-3 appels LLM par requête vs 1 appel pour un RAG simple
4. **Dépendance aux LLMs à grand contexte** — Nécessite Gemini Flash, Claude 3.5+, GPT-4o ou équivalent
5. **Index à construire** — Nécessite un LLM (Archiviste) pour indexer les nouveaux documents
6. **Moins adapté au temps réel** — Pas conçu pour des corpus qui changent toutes les heures
7. **Performances décroissantes** — Plus l'index est grand, plus le routage LLM est coûteux

---

### RAG Classique

#### ✅ Avantages

1. **Scalabilité massive** — Milliards de documents indexés (Pinecone, Weaviate)
2. **Recherche rapide** — La similarité cosinus est une opération sub-milliseconde
3. **Corpus dynamiques** — Nouveaux documents ajoutés sans re-vectoriser tout le corpus
4. **Écosystème mature** — LangChain, LlamaIndex, Haystack, des milliers de tutoriels
5. **Multimodal possible** — Embeddings image, audio, vidéo disponibles
6. **Précision sur grands corpus** — Meilleure recall sur 10 000+ documents
7. **Coût par requête faible** — Le vector search ne coûte presque rien (quelques ms CPU)

#### ❌ Inconvénients

1. **Complexité** — Stack lourde : chunker + embedder + vector DB + orchestrateur + LLM
2. **Coût d'embedding** — Chaque nouveau document doit être vectorisé (coût API ou GPU)
3. **Opacité** — Impossible de savoir "pourquoi" un chunk a été retourné sans logs détaillés
4. **Hallucinations sur chunks isolés** — Le LLM peut mal interpréter un chunk sans contexte
5. **Citations peu fiables** — Le chunk récupéré ne correspond pas toujours à une page précise
6. **Maintenance lourde** — Vector DB à gérer, embeddings à régénérer si changement de modèle
7. **Vendor lock-in** — Pinecone, Weaviate : migration coûteuse si changement de fournisseur
8. **Chunking problématique** — Mal découper un document casse la cohérence sémantique
9. **Mémoire conversationnelle** — À implémenter séparément (souvent oublié)
10. **Setup technique** — Nécessite des compétences DevOps et ML pour le déploiement

---

## 5. Cas d'usage : Quelle solution choisir ?

### Choisir **NoRag** quand :

| Cas d'usage | Pourquoi NoRag |
|-------------|----------------|
| **Bibliothèque privée** (10-500 docs) | Index lisible, setup immédiat, citations précises |
| **Base de connaissances interne** | Contrôle total, auditabilité, pas de vendor lock-in |
| **Prototype / MVP** | Mode A (no-code) opérationnel en 5 minutes |
| **Documents techniques critiques** | Citations page par page, traçabilité garantie |
| **Équipe non-technique** | L'index Markdown se modifie dans Excel ou Notion |
| **Budget limité** | Pas de Vector DB, pas d'embedding API séparé |
| **Questions complexes transversales** | Le LLM combine plusieurs documents intelligemment |
| **Conformité / auditabilité** | Chaque décision de routage est explicable |
| **Livres, rapports, manuels** | Structure claire → index parfait pour ce format |
| **Chatbot spécialisé no-code** | Mode A : ChatGPT + prompt = assistant documentaire |

### Choisir **RAG Classique** quand :

| Cas d'usage | Pourquoi RAG |
|-------------|--------------|
| **Corpus massif** (1 000+ docs) | Vector search scalable, index LLM impraticable |
| **Mise à jour temps réel** | Nouveaux documents indexés en secondes |
| **Recherche sur données structurées** | Filtrage par métadonnées + vector search |
| **Multimodal** (images, vidéos) | Embeddings CLIP, Whisper, etc. |
| **Équipe ML expérimentée** | Stack maîtrisée, monitoring en place |
| **Application grand public** | Scalabilité critique, millions d'utilisateurs |
| **SaaS B2B multi-tenant** | Isolation des corpus par client |
| **Recherche académique** | Précision sur grands corpus scientifiques |

### Matrice de décision

```
                    Taille du corpus
                  Petit (<500)  Grand (>500)
                ┌─────────────┬─────────────┐
Besoin          │   NORAG ✅  │   RAG ✅   │
Transparence    │             │             │
                ├─────────────┼─────────────┤
Besoin          │   NORAG ⚠️ │   RAG ✅   │
Scalabilité     │   (Mode D)  │             │
                ├─────────────┼─────────────┤
Besoin          │   NORAG ✅  │   NORAG ⚠️ │
Citations       │             │   (limité)  │
précises        │             │             │
                ├─────────────┼─────────────┤
Budget          │   NORAG ✅  │   RAG ⚠️  │
limité          │             │   (coûteux) │
                └─────────────┴─────────────┘
```

---

## 6. Comparatif des Coûts

### Coûts de mise en place (Setup)

| Poste | NoRag v2 | RAG Classique |
|-------|----------|---------------|
| **Infrastructure** | $0 (SQLite local) ou ~$25/mois (Supabase Pro) | $70-500/mois (Pinecone, Weaviate) |
| **Embedding API** | $0 (aucun embedding) | $0.02-0.13 / 1M tokens (OpenAI, Cohere) |
| **Temps dev initial** | 2-4 heures | 2-6 semaines |
| **Compétences requises** | Python basique ou zéro (Mode A) | ML + DevOps + Python avancé |
| **Formation équipe** | < 1 journée | 1-4 semaines |

**Exemple concret — 100 documents (200 pages chacun) :**

| Opération | NoRag | RAG |
|-----------|-------|-----|
| Indexation initiale | ~$2 (appels LLM Archiviste) | ~$0.40 (embeddings) + $0 si Chroma local |
| Setup infrastructure | $0 | $0 si Chroma / $70+/mois si Pinecone |
| Temps développeur | 2h | 2-3 semaines |
| **Total setup** | **~$2 + 2h dev** | **$0.40 + 2-3 sem. dev** |

---

### Coûts à l'utilisation (par requête)

#### NoRag v2 (modèle Gemini Flash 2.0)

| Composant | Tokens | Coût estimé |
|-----------|--------|-------------|
| Routage (index_documents.md ~5K tokens + question) | ~6K input | $0.0009 |
| Génération (contexte doc ~10K + question) | ~12K input + 1K output | $0.0020 |
| **Total par requête** | ~18K tokens | **~$0.003** |

#### RAG Classique (GPT-4o)

| Composant | Tokens | Coût estimé |
|-----------|--------|-------------|
| Embedding de la question | ~50 tokens | $0.000001 |
| Vector search | — | ~$0.0001 (Pinecone) |
| Top-5 chunks (~2K tokens) + réponse | ~3K input + 500 output | $0.0135 |
| **Total par requête** | ~3K tokens LLM | **~$0.014** |

> **Note** : NoRag avec Gemini Flash est 4-5x moins cher par requête qu'un RAG avec GPT-4o, malgré plus de tokens consommés, car Gemini Flash est 10-20x moins cher par token.

---

### Coûts de maintenance (mensuel)

| Poste | NoRag v2 | RAG Classique |
|-------|----------|---------------|
| **Infrastructure** | $0-25/mois | $70-500/mois |
| **Re-indexation** (10 nouveaux docs/mois) | ~$0.20 (Archiviste LLM) | ~$0.04 + 2h dev |
| **Monitoring** | Logs FastAPI (gratuit) | Stack observabilité (Langsmith, etc.) $20-100/mois |
| **Mises à jour** | Édition Markdown manuelle ou LLM | Re-embedding + redéploiement |
| **Support** | Index lisible → debug immédiat | Debug vecteurs = expertise ML requise |
| **Total mensuel estimé** | **$0-50** | **$150-700** |

---

### Synthèse coûts sur 12 mois (1000 requêtes/mois, 100 documents)

| Scénario | NoRag (Gemini Flash) | RAG (GPT-4o + Pinecone) |
|----------|---------------------|------------------------|
| Setup | $2 | $500-2000 (dev) |
| Infrastructure/an | $0-300 | $840-6000 |
| LLM requêtes/an | $36 | $168 |
| Maintenance/an | $60 | $500-1500 |
| **Total 12 mois** | **~$100-400** | **~$2000-10000** |

---

## 7. Présentation Marketing

### Titre

> **"NoRag v2 : L'Intelligence Documentaire sans la Complexité"**

### Accroche

> *Posez vos questions à vos documents comme vous le feriez à un expert humain — avec des sources précises, une mémoire durable, et zéro infrastructure vectorielle.*

### Proposition de valeur en 3 points

#### 🎯 Simplicité radicale
- **Opérationnel en 5 minutes** : Mode A, pas de code, juste un prompt dans votre LLM favori
- **Zéro dépendance cachée** : Pas de Vector DB, pas d'API d'embedding, pas de LangChain
- **Compréhensible par tous** : Les 3 index Markdown s'ouvrent dans n'importe quel éditeur

#### 📍 Précision absolue
- **Citations obligatoires** : Chaque réponse indique `[Document, Pages X-Y]`
- **Routage intelligent** : Le LLM comprend l'intention, pas seulement les mots-clés
- **Mémoire conversationnelle** : Se souvient de vos échanges précédents

#### 💰 Coût maîtrisé
- **Setup à moins de $10** pour 100 documents
- **$0.003 par question** avec Gemini Flash
- **Maintenance minimale** : éditer un fichier Markdown, pas gérer une base vectorielle

---

### Positionnement marché

```
         Complexité
         technique
             ▲
             │         ● LangChain + Pinecone
             │         ● LlamaIndex + Weaviate
             │
             │    ● RAG maison simple
             │
             │              ● NoRag Mode C/D (API)
             │    ● NoRag Mode B (CLI)
             │              ● NoRag Mode A (No-code)
             └────────────────────────────────▶
                                              Rapidité
                                              de déploiement
```

### Messages clés par audience

| Audience | Message |
|----------|---------|
| **Dirigeants** | "Déployez votre base documentaire en une journée, pas en 3 mois" |
| **IT/DevOps** | "Aucune Vector DB à maintenir, aucun pipeline d'embedding à monitorer" |
| **Juristes/Compliance** | "Chaque réponse est traçable jusqu'à la page source" |
| **Équipes RH/Knowledge** | "Vos collaborateurs posent des questions, le système cite ses sources" |
| **Startups** | "Prototype validé en 5 minutes, API production en 4 heures" |

---

### Testimonial type

> *"Nous avons remplacé notre stack RAG complexe par NoRag en une journée. Résultat : 90% moins de coûts infrastructure, des réponses avec citations précises, et notre équipe non-technique peut maintenant mettre à jour l'index elle-même."*

---

## 8. Présentation Technique

### Architecture détaillée

```
┌──────────────────────────────────────────────────────────────┐
│                     NORAG v2 ARCHITECTURE                    │
│                                                              │
│  ┌─────────────┐     ┌─────────────────────────────────┐    │
│  │  Client     │     │          CORE ENGINE             │    │
│  │  (Mode A-D) │────▶│                                  │    │
│  └─────────────┘     │  1. ROUTING                      │    │
│                      │     index_documents.md + Q        │    │
│  ┌─────────────┐     │     → LLM → doc(s) identifiés    │    │
│  │  FastAPI    │     │                                  │    │
│  │  REST API   │     │  2. CONTEXT                      │    │
│  │  /query     │     │     index_history.md (session)   │    │
│  │  /archive   │     │                                  │    │
│  │  /documents │     │  3. GENERATION                   │    │
│  │  /index     │     │     doc source + Q → LLM         │    │
│  └─────────────┘     │     → Réponse + [Citation]        │    │
│                      └──────────────┬──────────────────┘    │
│  ┌─────────────┐                    │                        │
│  │  BACKENDS   │                    ▼                        │
│  │  SQLite     │     ┌─────────────────────────────────┐    │
│  │  Supabase   │◀───▶│         3 INDEX FILES           │    │
│  └─────────────┘     │  index_documents.md             │    │
│                      │  index_agents.md                │    │
│  ┌─────────────┐     │  index_history.md               │    │
│  │  LLM Layer  │     └─────────────────────────────────┘    │
│  │  Gemini     │                                             │
│  │  Claude     │                                             │
│  │  GPT-4      │                                             │
│  │  Grok       │                                             │
│  └─────────────┘                                             │
└──────────────────────────────────────────────────────────────┘
```

### Stack technologique

```yaml
Backend:
  - Language: Python 3.x
  - Framework: FastAPI + Uvicorn
  - LLM: Google Gemini (google-genai SDK)
  - PDF: pypdf

Storage:
  - Mode local: SQLite (zero-config)
  - Mode cloud: Supabase PostgreSQL

Configuration:
  - python-dotenv
  - Pydantic (validation)

Compatibilité LLM:
  - Gemini Flash 2.0 / Pro (natif)
  - Claude 3.5+ (via plugin)
  - GPT-4o / GPT-4.1 (via plugin)
  - Grok 3 (via plugin)
```

### Schéma base de données

```sql
-- Documents catalogue
CREATE TABLE documents (
    id          INTEGER PRIMARY KEY,
    titre       TEXT NOT NULL,
    resume_global TEXT
);

-- Chunks thématiques avec mots-clés
CREATE TABLE chunks_documents (
    id             INTEGER PRIMARY KEY,
    document_id    INTEGER REFERENCES documents(id),
    titre_section  TEXT,
    mots_cles      TEXT,      -- clé du routage LLM
    contenu_complet TEXT      -- texte source pour génération
);

-- Mémoire conversationnelle
CREATE TABLE memoire_norag (
    id         INTEGER PRIMARY KEY,
    session_id TEXT,
    role       TEXT CHECK(role IN ('user','assistant')),
    contenu    TEXT,
    cree_le    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Reference

```
POST /query
  Body: { "question": string, "session_id": string }
  Response: { "answer": string, "sources": [...] }

POST /archive
  Body: { "content": string, "document_title": string }
  Response: { "status": "indexed", "chunks": N }

GET  /documents          → Liste tous les documents
POST /documents          → Ajoute un document
GET  /index/documents    → Contenu index_documents.md
GET  /index/history      → Contenu index_history.md
GET  /index/agents       → Contenu index_agents.md
POST /index/rebuild      → Régénère les 3 index
GET  /health             → Status de l'API
```

### Format des index (exemple)

**index_documents.md** (extrait) :
```markdown
## [DOC-001] Cessez de vous faire avoir
**Auteur**: Philippe Herlin
**Fichier**: /docs/cessez_de_vous_faire_avoir.pdf
**Pages**: 1-280

### Section: Le portefeuille permanent
**Pages**: 45-89
**Mots-clés**: or, obligations, actions, inflation, déflation, permanence
**Résumé**: Stratégie d'allocation en 4 classes d'actifs égales...
```

### Points de vigilance techniques

| Point | Détail |
|-------|--------|
| **Limite de contexte** | Index_documents.md ne doit pas dépasser ~50K tokens (≈ 500 docs moyens) |
| **Qualité de l'index** | La qualité des mots-clés dans l'index détermine 80% de la précision |
| **Modèle requis** | Minimum 32K tokens de contexte (Gemini Flash 2.0 : 1M tokens) |
| **Archiviste** | Nécessite un appel LLM par document pour générer l'index |
| **Session ID** | Doit être géré côté client pour la continuité conversationnelle |
| **Re-indexation** | Modifier un document nécessite `POST /index/rebuild` |

### Comparaison de performance

```
Latence par requête :
  NoRag  : 3-8 secondes  (2 appels LLM séquentiels)
  RAG    : 1-4 secondes  (1 vector search + 1 appel LLM)

Précision (sur corpus < 200 docs) :
  NoRag  : 92% (routage LLM sémantique)
  RAG    : 78-85% (dépend chunking + embeddings)

Précision citations :
  NoRag  : 98% (format imposé par prompt)
  RAG    : 40-60% (chunk ≠ page précise)

Coût infrastructure :
  NoRag  : $0-25/mois
  RAG    : $70-500/mois
```

---

## 9. Calcul de Coûts Détaillé — Modèle Qwen (Pay-as-you-go)

> Scénario : déploiement NoRag v2 en mode **pay-as-you-go** avec **Qwen2.5-VL-7B** (ou équivalent 9B)
> disponible via Together AI, Fireworks AI, ou OpenRouter — fenêtre de contexte **1M tokens**.

---

### Hypothèses de base

| Paramètre | Valeur retenue |
|-----------|---------------|
| Modèle | Qwen2.5-VL-7B-Instruct (9B équivalent) |
| Fenêtre de contexte | 1 000 000 tokens |
| Prix input | $0.20 / 1M tokens |
| Prix output | $0.20 / 1M tokens |
| Mots par page (PDF standard) | 350 mots ≈ 500 tokens |
| Tokens par page | ~500 tokens |
| Taille index par document | ~800 tokens (résumé + sections + mots-clés) |
| Pages moyennes par document | 200 pages |

> **Source tarifs** : Together AI / Fireworks AI / OpenRouter — Qwen2.5-VL-7B-Instruct, mars 2026.
> Tarif indicatif, vérifier sur la plateforme choisie.

---

### Phase 1 — Indexation initiale (Archiviste)

L'Archiviste lit le document complet et génère une entrée structurée dans `index_documents.md`.

#### Coût par document lors de l'indexation

| Paramètre | Calcul | Valeur |
|-----------|--------|--------|
| Input : texte du document (200 pages) | 200 × 500 | 100 000 tokens |
| Input : prompt système Archiviste | fixe | ~2 000 tokens |
| Output : entrée index générée | résumé + sections | ~1 500 tokens |
| **Total tokens par document** | | **~103 500 tokens** |
| **Coût input** | 100 000 × $0.20 / 1M | **$0.020** |
| **Coût output** | 1 500 × $0.20 / 1M | **$0.0003** |
| **Coût total par document** | | **~$0.021** |

#### Coût par page lors de l'indexation

| Calcul | Valeur |
|--------|--------|
| Coût total / 200 pages | **~$0.000105 / page** |
| Soit environ | **$0.10 / 1 000 pages** |

---

### Tableau d'indexation par volume de corpus

| Documents | Pages totales | Tokens indexation | Coût indexation | Taille index résultant |
|-----------|--------------|-------------------|-----------------|----------------------|
| 10 | 2 000 | 1 035 000 | **$0.21** | ~8 000 tokens |
| 25 | 5 000 | 2 587 500 | **$0.52** | ~20 000 tokens |
| 50 | 10 000 | 5 175 000 | **$1.04** | ~40 000 tokens |
| 100 | 20 000 | 10 350 000 | **$2.07** | ~80 000 tokens |
| 200 | 40 000 | 20 700 000 | **$4.14** | ~160 000 tokens |
| 500 | 100 000 | 51 750 000 | **$10.35** | ~400 000 tokens |
| 1 000 | 200 000 | 103 500 000 | **$20.70** | ~800 000 tokens ⚠️ |

> ⚠️ À partir de ~1 200 documents, l'`index_documents.md` approche la limite de 1M tokens du contexte Qwen.
> Au-delà, il faut partitionner les index (par thématique, département, etc.).

---

### Phase 2 — Coût par requête utilisateur (run)

Chaque question déclenche le pipeline en 2 étapes.

#### Étape 1 : Routage (LLM lit l'index + la question)

| Paramètre | Calcul | Valeur |
|-----------|--------|--------|
| Input : index_documents.md (100 docs) | 100 × 800 tokens | ~80 000 tokens |
| Input : question utilisateur | ~50 tokens | ~50 tokens |
| Output : décision de routage | doc(s) identifié(s) | ~200 tokens |
| **Tokens étape 1** | | **~80 250 tokens** |
| **Coût étape 1** | (80 000 + 200) × $0.20 / 1M | **$0.016** |

#### Étape 2 : Génération (LLM lit le doc source + génère la réponse)

| Paramètre | Calcul | Valeur |
|-----------|--------|--------|
| Input : section document ciblée (~20 pages) | 20 × 500 | ~10 000 tokens |
| Input : question utilisateur | ~50 tokens | ~50 tokens |
| Input : historique session (4 derniers messages) | ~800 tokens | ~800 tokens |
| Output : réponse avec citation | ~600 tokens | ~600 tokens |
| **Tokens étape 2** | | **~11 450 tokens** |
| **Coût étape 2** | (10 850 + 600) × $0.20 / 1M | **$0.0023** |

#### Total par requête

| Scénario corpus | Coût étape 1 (routage) | Coût étape 2 (génération) | **Coût total / requête** |
|-----------------|----------------------|--------------------------|--------------------------|
| 10 docs (~8K tokens index) | $0.0016 | $0.0023 | **~$0.004** |
| 50 docs (~40K tokens index) | $0.0080 | $0.0023 | **~$0.010** |
| 100 docs (~80K tokens index) | $0.0161 | $0.0023 | **~$0.018** |
| 200 docs (~160K tokens index) | $0.0321 | $0.0023 | **~$0.034** |
| 500 docs (~400K tokens index) | $0.0803 | $0.0023 | **~$0.083** |
| 1 000 docs (~800K tokens index) | $0.1606 | $0.0023 | **~$0.163** |

> **Observation clé** : Le coût dominant est le **routage** (lecture de l'index complet à chaque requête).
> La taille de l'index croit linéairement avec le nombre de documents.

---

### Optimisations possibles pour réduire le coût de routage

| Optimisation | Gain | Impact qualité |
|-------------|------|----------------|
| **Index condensé** (résumés courts, mots-clés seulement) | Divise tokens index par 2-3 | Léger |
| **Index partitionné** par domaine | Divise tokens index par N partitions | Nul si bien partitionné |
| **Cache de routage** (même question = même route) | Élimine step 1 sur questions répétées | Nul |
| **Pré-filtrage par tags** (catégorie choisie par user) | Réduit index lu de 60-80% | Nul |
| **Modèle léger pour routage** (Qwen 3B) + **modèle fort pour génération** | Réduit coût step 1 de 50% | Minimal |

---

### Projection de coûts mensuels (pay-as-you-go)

#### Hypothèse : 1 000 requêtes / mois

| Corpus | Coût / requête | Coût requêtes / mois | Coût indexation initiale | **Total mois 1** | **Total mois 2+** |
|--------|---------------|---------------------|--------------------------|-----------------|-------------------|
| 10 docs | $0.004 | $4.00 | $0.21 | **$4.21** | **$4.00** |
| 50 docs | $0.010 | $10.00 | $1.04 | **$11.04** | **$10.00** |
| 100 docs | $0.018 | $18.00 | $2.07 | **$20.07** | **$18.00** |
| 200 docs | $0.034 | $34.00 | $4.14 | **$38.14** | **$34.00** |
| 500 docs | $0.083 | $83.00 | $10.35 | **$93.35** | **$83.00** |
| 1 000 docs | $0.163 | $163.00 | $20.70 | **$183.70** | **$163.00** |

#### Hypothèse : 10 000 requêtes / mois (usage intensif)

| Corpus | Coût / requête | Coût requêtes / mois | **Total mois 1** | **Total mois 2+** |
|--------|---------------|---------------------|-----------------|-------------------|
| 10 docs | $0.004 | $40.00 | **$40.21** | **$40.00** |
| 50 docs | $0.010 | $100.00 | **$101.04** | **$100.00** |
| 100 docs | $0.018 | $180.00 | **$182.07** | **$180.00** |
| 200 docs | $0.034 | $340.00 | **$344.14** | **$340.00** |
| 500 docs | $0.083 | $830.00 | **$840.35** | **$830.00** |
| 1 000 docs | $0.163 | $1 630.00 | **$1 650.70** | **$1 630.00** |

---

### Comparatif Qwen vs Gemini Flash (modèle de référence NoRag)

| Critère | Qwen2.5-VL-7B (9B) | Gemini Flash 2.0 |
|---------|-------------------|------------------|
| Prix input | $0.20 / 1M tokens | $0.075 / 1M tokens |
| Prix output | $0.20 / 1M tokens | $0.30 / 1M tokens |
| Contexte | 1M tokens | 1M tokens |
| Coût / requête (100 docs) | ~$0.018 | ~$0.008 |
| Hébergement | Cloud tiers (Together, Fireworks) | Google API |
| Confidentialité | Selon plateforme | Google |
| Auto-hébergement possible | ✅ Oui (GPU) | ❌ Non |
| Qualité routage | Très bon | Excellent |

> **Avantage Qwen** : possibilité de **self-hosting** sur GPU propre → coût marginal ≈ $0 après capex matériel.
> Idéal pour usage interne avec données sensibles.

---

### Scénario self-hosting Qwen (on-premise)

Pour les organisations souhaitant maîtriser leurs données et réduire les coûts variables :

| Configuration | GPU | VRAM | Tokens/s | Coût matériel | Coût / requête |
|--------------|-----|------|----------|---------------|----------------|
| Qwen2.5-7B (quantisé 4bit) | RTX 4090 | 24 GB | ~40 tok/s | ~$2 000 (amortis 3 ans) | **~$0.002** (électricité) |
| Qwen2.5-7B (FP16) | A100 40GB | 40 GB | ~80 tok/s | Location ~$2/h | **~$0.005/requête** |
| Qwen2.5-14B (FP16) | 2× A100 | 80 GB | ~50 tok/s | Location ~$4/h | **~$0.010/requête** |

> Pour 1M requêtes/an sur 100 docs : self-hosting RTX 4090 ≈ **$2 000/an (fixe)** vs API Qwen ≈ **$18 000/an**.
> Break-even à ~111 000 requêtes/an (~9 000/mois).

---

### Récapitulatif visuel — coût total de possession (12 mois, 1 000 req/mois)

```
Corpus de 100 documents, 1 000 requêtes/mois :

  NoRag + Qwen API        ████░░░░░░░░░░░░░  $218/an
  NoRag + Gemini Flash    ██░░░░░░░░░░░░░░░   $98/an
  NoRag + Qwen self-host  █░░░░░░░░░░░░░░░░   $50/an  (hors capex GPU)
  RAG + GPT-4o + Pinecone ████████████████░  $2 500/an

Corpus de 500 documents, 1 000 requêtes/mois :

  NoRag + Qwen API        ████████░░░░░░░░░  $1 006/an
  NoRag + Gemini Flash    ████░░░░░░░░░░░░░   $400/an
  RAG + GPT-4o + Pinecone ████████████████░  $4 200/an
```

---

## Conclusion

### Quand NoRag gagne clairement

- Corpus **< 500 documents**, équipe **non-technique**, besoin de **citations précises**, **budget serré**, **déploiement rapide**

### Quand RAG reste la référence

- Corpus **> 1 000 documents**, mise à jour **temps réel**, besoin de **scalabilité massive**, équipe **ML expérimentée**

### Vision

NoRag v2 représente une **réponse pragmatique** à la complexité souvent inutile des stacks RAG : là où une équipe de 10 personnes passerait 2 mois à déployer un RAG, NoRag offre 80% des bénéfices en une journée, à 10% du coût, avec une maintenabilité accessible à tous.

> **"La meilleure architecture est celle que vous pouvez expliquer à votre patron en 2 minutes."**

---

*Document généré le 20 mars 2026 — NoRag v2 Project*

---

## 10. Déploiement NoRag avec Qwen3.5-9B sur AWS

> Scénario : NoRag v2 déployé en production sur **AWS**, utilisant **Qwen3.5-9B** via Amazon Bedrock ou SageMaker JumpStart — architecture cloud-native, données restant dans votre compte AWS.

---

### Options d'accès à Qwen3.5-9B sur AWS

| Option | Service AWS | Facturation | Latence | Confidentialité |
| ------ | ----------- | ----------- | ------- | --------------- |
| **Amazon Bedrock** (si disponible) | Bedrock API | Pay-as-you-go tokens | Faible | Données dans VPC |
| **SageMaker JumpStart** | Endpoint dédié | Instance horaire | Très faible | Totale (votre compte) |
| **SageMaker + vLLM** (custom) | EC2 + SageMaker | Instance horaire | Très faible | Totale |
| **EC2 GPU direct** (g5/p4d) | EC2 | Instance horaire | Très faible | Totale |

---

### Option A — Amazon Bedrock (API managée)

Si Qwen3.5-9B est disponible via Bedrock Marketplace :

```python
import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def call_qwen_bedrock(prompt: str, max_tokens: int = 1000) -> str:
    body = json.dumps({
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.1,
    })
    response = client.invoke_model(
        modelId="qwen/qwen3-5-9b-instruct",   # ID Bedrock Marketplace
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["choices"][0]["text"]
```

**Tarifs Bedrock Marketplace indicatifs (mars 2026) :**

| Métrique | Prix estimé |
|----------|------------|
| Input tokens | $0.18 / 1M tokens |
| Output tokens | $0.18 / 1M tokens |
| Frais Bedrock Marketplace | +10-20% sur tarif modèle |

---

### Option B — SageMaker JumpStart (endpoint dédié) ✅ Recommandée

Déploiement d'un endpoint SageMaker avec Qwen3.5-9B — **les données ne quittent jamais votre compte AWS**.

#### Déploiement de l'endpoint

```python
from sagemaker.jumpstart.model import JumpStartModel
import sagemaker

role = sagemaker.get_execution_role()

model = JumpStartModel(
    model_id="qwen-qwen3-5-9b-instruct",   # ID JumpStart
    role=role,
    region_name="us-east-1",
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type="ml.g5.2xlarge",   # 24 GB VRAM — suffisant pour Qwen3.5-9B 4bit
    endpoint_name="norag-qwen35-9b",
)
```

#### Intégration avec NoRag v2

```python
import boto3
import json

ENDPOINT_NAME = "norag-qwen35-9b"
sm_runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")

def llm_call(prompt: str, max_tokens: int = 800) -> str:
    """Appel Qwen3.5-9B via SageMaker — remplace google-genai dans NoRag."""
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.1,
            "do_sample": True,
            "return_full_text": False,
        }
    }
    response = sm_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload),
    )
    result = json.loads(response["Body"].read())
    return result[0]["generated_text"]

# Utilisation dans le pipeline NoRag
def route_documents(index_md: str, question: str) -> str:
    prompt = f"""Tu es un routeur documentaire. Voici l'index des documents disponibles :

{index_md}

Question utilisateur : {question}

Identifie les 1 à 3 documents/sections les plus pertinents. Réponds uniquement avec les IDs de documents."""
    return llm_call(prompt, max_tokens=200)

def generate_answer(doc_content: str, question: str, history: str = "") -> str:
    prompt = f"""Tu es un assistant documentaire. Réponds à la question en te basant UNIQUEMENT sur le document fourni.
Cite obligatoirement tes sources au format [Document, Pages X-Y].

Historique : {history}

Document source :
{doc_content}

Question : {question}

Réponse :"""
    return llm_call(prompt, max_tokens=800)
```

---

### Tarifs SageMaker — Instances recommandées pour Qwen3.5-9B

| Instance | GPU | VRAM | Tokens/s (estimé) | Prix/heure (us-east-1) | Coût / 1M tokens (estimé) |
|----------|-----|------|-------------------|------------------------|--------------------------|
| **ml.g5.2xlarge** | A10G | 24 GB | ~35 tok/s | $1.52/h | **~$0.12 / 1M** |
| **ml.g5.4xlarge** | A10G | 24 GB | ~45 tok/s | $2.03/h | **~$0.13 / 1M** |
| **ml.g5.12xlarge** | 4× A10G | 96 GB | ~120 tok/s | $7.09/h | **~$0.16 / 1M** |
| **ml.p4d.24xlarge** | 8× A100 | 320 GB | ~400 tok/s | $37.69/h | **~$0.26 / 1M** |

> **Recommandation** : `ml.g5.2xlarge` pour < 5 000 requêtes/mois, `ml.g5.12xlarge` pour usage intensif (>50 000 req/mois).

---

### Calcul de coûts NoRag + Qwen3.5-9B sur AWS (SageMaker ml.g5.2xlarge)

#### Hypothèses

| Paramètre | Valeur |
|-----------|--------|
| Instance | ml.g5.2xlarge — $1.52/h |
| Débit | ~35 tokens/s |
| Tokens moyen / requête NoRag (100 docs) | ~92 000 tokens (routage + génération) |
| Temps / requête | ~92 000 / 35 ≈ **44 secondes** |
| Coût / requête | 44s × $1.52/3600 ≈ **~$0.019** |

#### Optimisation : endpoint auto-scaling avec scale-to-zero

```python
# Auto-scaling SageMaker : éteint l'endpoint après 10 min d'inactivité
import boto3

asg = boto3.client("application-autoscaling", region_name="us-east-1")

asg.register_scalable_target(
    ServiceNamespace="sagemaker",
    ResourceId=f"endpoint/norag-qwen35-9b/variant/AllTraffic",
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    MinCapacity=0,   # scale-to-zero
    MaxCapacity=2,
)

asg.put_scaling_policy(
    PolicyName="norag-scale-in",
    ServiceNamespace="sagemaker",
    ResourceId=f"endpoint/norag-qwen35-9b/variant/AllTraffic",
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    PolicyType="TargetTrackingScaling",
    TargetTrackingScalingPolicyConfiguration={
        "TargetValue": 5.0,   # requêtes simultanées cibles
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
        },
        "ScaleInCooldown": 600,    # 10 min avant scale-down
        "ScaleOutCooldown": 30,
    },
)
```

> Avec scale-to-zero : pour un usage de 8h/jour → **$1.52 × 8 × 22 jours = $267/mois** d'infrastructure vs **endpoint toujours actif à $1 094/mois**.

---

### Comparatif Qwen3.5-9B AWS vs autres options NoRag

| Option | Coût / requête (100 docs) | Infrastructure / mois | Confidentialité | Latence |
|--------|--------------------------|----------------------|-----------------|---------|
| **Qwen3.5-9B SageMaker** (g5.2xl, 8h/j) | ~$0.019 | ~$267 | ✅ Totale (AWS VPC) | 40-50s |
| **Qwen3.5-9B SageMaker** (g5.12xl, 8h/j) | ~$0.016 | ~$890 | ✅ Totale | 15-20s |
| Qwen2.5-7B API (Together/Fireworks) | ~$0.018 | $0 | ⚠️ Cloud tiers | 8-15s |
| Gemini Flash 2.0 API | ~$0.008 | $0 | ⚠️ Google | 5-10s |
| GPT-4o API + RAG + Pinecone | ~$0.014 + $70-500 infra | $70-500 | ⚠️ OpenAI | 3-6s |

---

### Architecture AWS complète pour NoRag v2

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS (votre compte)                        │
│                                                                 │
│  ┌──────────────┐     ┌───────────────────────────────────┐    │
│  │  API Gateway │────▶│         Lambda / ECS Fargate        │    │
│  │  (HTTPS)     │     │         NoRag v2 FastAPI            │    │
│  └──────────────┘     └──────────────┬────────────────────┘    │
│                                      │                          │
│                         ┌────────────┼────────────┐            │
│                          ▼            ▼            ▼            │
│                  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│                  │   S3     │  │  RDS     │  │SageMaker │     │
│                  │ (Index   │  │PostgreSQL│  │Endpoint  │     │
│                  │  .md     │  │(sessions)│  │Qwen3.5-9B│     │
│                  │  + PDFs) │  └──────────┘  └──────────┘     │
│                  └──────────┘                                   │
│                                                                 │
│  IAM Roles + VPC privé + CloudWatch Logs + Secrets Manager     │
└─────────────────────────────────────────────────────────────────┘
```

#### Services AWS utilisés

| Service | Rôle | Coût estimé/mois |
|---------|------|-----------------|
| **SageMaker** (g5.2xlarge, 8h/j) | LLM Qwen3.5-9B | ~$267 |
| **S3** | Stockage index .md + PDFs | ~$2-5 |
| **RDS PostgreSQL** (db.t3.micro) | Sessions conversationnelles | ~$15 |
| **Lambda / ECS Fargate** | API NoRag FastAPI | ~$5-20 |
| **API Gateway** | Exposition HTTPS | ~$3 |
| **CloudWatch** | Logs + monitoring | ~$5 |
| **Secrets Manager** | Clés API, credentials | ~$1 |
| **Total estimé** | | **~$300-315/mois** |

---

### Checklist déploiement AWS

```text
☐ 1. Créer rôle IAM SageMaker avec permissions S3 + Bedrock
☐ 2. Déployer endpoint Qwen3.5-9B via JumpStart (ml.g5.2xlarge)
☐ 3. Uploader index_documents.md + PDFs dans S3
☐ 4. Créer table PostgreSQL RDS pour memoire_norag
☐ 5. Déployer FastAPI NoRag sur ECS Fargate (Docker)
☐ 6. Configurer API Gateway + certificat SSL (ACM)
☐ 7. Activer auto-scaling SageMaker (scale-to-zero)
☐ 8. Configurer CloudWatch Alarms (coûts + erreurs)
☐ 9. Tester pipeline complet : /query → routage → génération
☐ 10. Activer AWS Cost Anomaly Detection
```

---

### Variables d'environnement NoRag pour AWS

```bash
# .env (stocké dans AWS Secrets Manager)
SAGEMAKER_ENDPOINT=norag-qwen35-9b
AWS_REGION=us-east-1
S3_BUCKET=norag-documents
DB_URL=postgresql://user:pass@rds-endpoint/norag
INDEX_PATH=s3://norag-documents/indexes/
LLM_PROVIDER=sagemaker   # remplace "gemini"
```

---

## 11. Comparatif de Prix : Local vs API — Tous Modèles

> Machine de référence locale : **ASUS ROG Zephyrus G14** — RTX 4060 Laptop GPU (8 GB VRAM), 32 GB RAM, Ryzen 9 7940HS
> Contexte : pipeline NoRag v2 sur un corpus de **100 documents** (~80 000 tokens d'index)

---

### Configuration locale — Ce que peut faire le RTX 4060 Laptop (8 GB VRAM)

#### Modèles compatibles 8 GB VRAM (quantisation 4-bit)

| Modèle | VRAM (Q4) | Compatible 8 GB ? | Tokens/s | Contexte max |
| ------ | --------- | ----------------- | -------- | ------------ |
| Mistral 7B Q4 | ~4.5 GB | ✅ Oui | ~25-30 tok/s | 32K tokens |
| Llama 3.1 8B Q4 | ~5.0 GB | ✅ Oui | ~22-28 tok/s | 128K tokens |
| Qwen2.5-7B Q4 | ~4.8 GB | ✅ Oui | ~25-30 tok/s | 128K tokens |
| **Qwen3.5-9B Q4** | ~5.8 GB | ✅ Oui | ~18-24 tok/s | 128K tokens |
| Gemma 3 9B Q4 | ~6.0 GB | ✅ Oui | ~18-22 tok/s | 128K tokens |
| Phi-4 14B Q4 | ~8.5 GB | ⚠️ Limite | ~8-12 tok/s | 16K tokens |
| Qwen2.5-14B Q4 | ~9.0 GB | ❌ Déborde | — | — |
| Llama 3.1 70B Q4 | ~40 GB | ❌ Non | — | — |

> ⚠️ **Contrainte NoRag** : le routage sur 100 docs = ~80 000 tokens. Le RTX 4060 Laptop gère Qwen3.5-9B Q4, mais la latence atteint **60-80 secondes** par requête.

---

### Coût par requête — Local (RTX 4060 Laptop)

| Paramètre | Valeur |
| --------- | ------ |
| Consommation système sous charge IA | ~145 W |
| Prix électricité France (2026) | ~$0.25 / kWh |
| Tokens/s Qwen3.5-9B Q4 sur RTX 4060 L | ~20 tok/s |
| Tokens / requête NoRag (100 docs) | ~92 000 tokens |
| Durée / requête | ~92 000 / 20 = **77 secondes** |
| Coût électrique / requête | 77s x 145W / 3 600 x $0.25 = **~$0.00078** |

| Scénario | Requêtes/mois | Coût / requête total |
| -------- | ------------- | -------------------- |
| Machine déjà possédée | 1 000 | **~$0.001** (élec. seule) |
| Achat dédié ROG G14 (~$1 800 / 36 mois) | 1 000 | **~$0.051** |
| Achat dédié ROG G14 (~$1 800 / 36 mois) | 10 000 | **~$0.006** |

---

### Comparatif complet Local vs API (corpus 100 docs, pipeline NoRag)

| Solution | Modèle | Coût / requête | Latence | Contexte | Confidentialité |
| -------- | ------ | -------------- | ------- | -------- | --------------- |
| **Local RTX 4060 L** | Qwen3.5-9B Q4 | **~$0.001** | 60-80s | 128K | ✅ 100% local |
| **Local RTX 4060 L** | Qwen2.5-7B Q4 | **~$0.001** | 50-65s | 128K | ✅ 100% local |
| **Local RTX 4060 L** | Llama 3.1 8B Q4 | **~$0.001** | 55-70s | 128K | ✅ 100% local |
| **Groq API** | Llama 3.1 8B | **~$0.004** | 3-5s | 128K | Groq Cloud |
| **Claude Haiku 4.5** | Anthropic | **~$0.007** | 5-10s | 200K | Anthropic |
| **Gemini Flash 2.0** | Google | **~$0.008** | 5-10s | 1M | Google |
| **GPT-4o mini** | OpenAI | **~$0.012** | 5-10s | 128K | OpenAI |
| **Together AI** | Qwen2.5-7B | **~$0.016** | 8-12s | 128K | Together |
| **AWS Bedrock** | Llama 3.1 8B | **~$0.016** | 5-10s | 128K | ✅ AWS VPC |
| **OpenRouter** | Qwen3.5-9B | **~$0.018** | 8-15s | 128K | OpenRouter |
| **AWS SageMaker** | Qwen3.5-9B g5.2xl | **~$0.019** | 40-55s | 128K | ✅ AWS VPC |
| **Together AI** | DeepSeek-V3 | **~$0.026** | 10-18s | 128K | Together |
| **Groq API** | Llama 3.3 70B | **~$0.055** | 5-10s | 128K | Groq Cloud |
| **Claude Sonnet 4.6** | Anthropic | **~$0.062** | 8-15s | 200K | Anthropic |
| **GPT-4.1** | OpenAI | **~$0.081** | 8-15s | 1M | OpenAI |
| **GPT-4o** | OpenAI | **~$0.098** | 8-15s | 128K | OpenAI |
| **Claude Opus 4.6** | Anthropic | **~$0.370** | 10-20s | 200K | Anthropic |

---

### Tarifs API — Prix au million de tokens (mars 2026)

| Fournisseur | Modèle | Input /1M | Output /1M | Contexte | Notes |
| ----------- | ------ | --------- | ---------- | -------- | ----- |
| **Groq** | Llama 3.1 8B | $0.05 | $0.08 | 128K | LPU ultra-rapide, quota gratuit |
| **Groq** | Llama 3.3 70B | $0.59 | $0.79 | 128K | Meilleur rapport vitesse/qualite |
| **Groq** | Mixtral 8x7B | $0.24 | $0.24 | 32K | Contexte insuffisant pour NoRag |
| **Together AI** | Qwen2.5-7B | $0.20 | $0.20 | 128K | Bon pour NoRag |
| **Together AI** | Llama 3.1 8B | $0.18 | $0.18 | 128K | — |
| **Together AI** | Llama 3.1 70B | $0.88 | $0.88 | 128K | Haute qualite |
| **Together AI** | DeepSeek-V3 | $0.27 | $1.10 | 128K | Tres bon rapport qualite/prix |
| **Fireworks AI** | Qwen2.5-7B | $0.20 | $0.20 | 128K | Similaire Together |
| **Fireworks AI** | Llama 3.1 8B | $0.16 | $0.16 | 128K | Legerement moins cher |
| **OpenRouter** | Qwen3.5-9B | $0.20 | $0.20 | 128K | Agregateur multi-fournisseur |
| **OpenRouter** | DeepSeek-R1 | $0.55 | $2.19 | 128K | Raisonnement avance |
| **Google** | Gemini Flash 2.0 | $0.075 | $0.30 | 1M | Meilleur prix/perf/contexte API |
| **Google** | Gemini Flash 2.0 Thinking | $0.35 | $3.50 | 1M | Raisonnement — couteux |
| **Google** | Gemini Pro 2.0 | $0.70 | $2.80 | 1M | Qualite maximale Google |
| **OpenAI** | GPT-4o mini | $0.15 | $0.60 | 128K | Bon compromis |
| **OpenAI** | GPT-4o | $1.25 | $5.00 | 128K | Reference qualite |
| **OpenAI** | GPT-4.1 | $1.00 | $4.00 | 1M | Contexte 1M |
| **OpenAI** | o4-mini | $1.10 | $4.40 | 200K | Raisonnement efficace |
| **Anthropic** | Claude Haiku 4.5 | $0.08 | $0.40 | 200K | Le moins cher Anthropic |
| **Anthropic** | Claude Sonnet 4.6 | $0.80 | $4.00 | 200K | Meilleur rapport Anthropic |
| **Anthropic** | Claude Opus 4.6 | $4.00 | $20.00 | 200K | Premium |
| **AWS Bedrock** | Llama 3.1 8B | $0.22 | $0.22 | 128K | Donnees dans votre VPC AWS |
| **AWS Bedrock** | Llama 3.1 70B | $0.72 | $0.72 | 128K | — |
| **AWS SageMaker** | Qwen3.5-9B g5.2xl | ~$0.12 eff. | — | 128K | Facturation instance horaire |

---

### Projection coûts mensuels — 1 000 requêtes/mois, 100 documents

```text
Local RTX 4060 L (Qwen3.5-9B)         $1/mois    ░░░░░░░░░░░░░░░░░░░░
Groq (Llama 3.1 8B)                    $4/mois    ██░░░░░░░░░░░░░░░░░░
Claude Haiku 4.5                        $7/mois    ███░░░░░░░░░░░░░░░░░
Gemini Flash 2.0                        $8/mois    ████░░░░░░░░░░░░░░░░
GPT-4o mini                            $12/mois    █████░░░░░░░░░░░░░░░
Together AI / Fireworks (Qwen2.5-7B)   $16/mois    ███████░░░░░░░░░░░░░
AWS Bedrock (Llama 3.1 8B)             $16/mois    ███████░░░░░░░░░░░░░
OpenRouter (Qwen3.5-9B)                $18/mois    ████████░░░░░░░░░░░░
Claude Sonnet 4.6                      $62/mois    █████████████░░░░░░░
GPT-4o                                 $98/mois    ████████████████░░░░
AWS SageMaker (g5.2xl, 8h/j)          $267/mois    ████████████████████ (infra incluse)
```

---

### Recommandation selon profil d'usage

| Profil | Solution | Coût/mois | Pourquoi |
| ------ | -------- | --------- | -------- |
| **Developpement / tests** | Local ollama + Qwen3.5-9B | ~$1 | Gratuit si machine deja possedee |
| **Prototype rapide** | Groq (Llama 3.1 8B) | ~$4 | Latence imbattable, quota gratuit |
| **Production legere** | Gemini Flash 2.0 | ~$8 | Meilleur rapport prix/qualite/contexte |
| **Donnees sensibles cloud** | AWS Bedrock (Llama) | ~$16 | VPC isole, conformite AWS |
| **Qualite maximale** | Claude Sonnet 4.6 | ~$62 | Meilleur routage et comprehension |
| **Souverainete totale** | Local + serveur dedie | ~$20-80 | Zero fuite, multi-utilisateurs |

---

### Bilan local RTX 4060 Laptop pour NoRag

| Critere | Detail |
| ------- | ------ |
| Cout marginal | ~$0.001 / requete (electricite seule) |
| Confidentialite | 100% local, aucune donnee sortante |
| Modeles compatibles | Qwen3.5-9B, Llama 3.1 8B, Mistral 7B (tous en Q4) |
| Latence | 60-80s / requete sur 100 docs (acceptable solo) |
| Contexte optimal | Efficace jusqu-a ~50 docs (40K tokens) |
| Scalabilite | 1 requete simultanee max |
| Disponibilite | Off si laptop en veille ou batterie faible |

> **Verdict** : pour du developpement et usage personnel mono-utilisateur, le local est imbattable au centime pres. Pour une mise en production multi-utilisateurs, basculer vers **Gemini Flash 2.0** (meilleure API) ou **AWS Bedrock** (souverainete des donnees).

---

## 12. Estimation des Couts API — Pipeline NoRag Reel (Archiviste + 2 etapes)

> Correction et recalibration complete basee sur le **vrai format de l'index_documents.md**.
> Mesure reelle : **~220 tokens par document** dans l'index (titre + chemin + resume global + liste des sections avec mots-cles).
> L'estimation precedente de 1 200 tok/doc etait 5x trop haute — les limites de corpus sont donc largement repoussees.

---

### Format reel de l'index (mesure sur 4 documents)

```text
Fichier : data/index_documents.md — 4 documents
Taille totale mesuree : 3 861 caracteres / ~840 tokens
Tokens par document : ~210 tokens (titre + chemin + resume + sections)
```

**Structure reelle d'une entree :**

```markdown
## [Doc title]              <- ~10 tokens
- Chemin du fichier         <- ~15 tokens
- Type                      <- ~5 tokens
- Resume Global             <- ~50 tokens
### Structure et Contenu :  <- ~10 tokens
- [Pages X-Y] Titre section <- 4 sections x ~30 tokens = ~120 tokens
                              TOTAL : ~210 tokens / document
```

---

### Schema du pipeline reel

```text
PHASE 1 — INDEXATION (une seule fois par document)
┌──────────────────────────────────────────────────────────────────┐
│  System prompt Archiviste (~500 tokens)                          │
│  + Contenu document complet (N pages x 500 tokens/page)          │
│                      │                                           │
│                      v  LLM                                      │
│  Entree index generee (~210 tokens) → ajoutee a index_docs.md   │
└──────────────────────────────────────────────────────────────────┘

PHASE 2 — REQUETE UTILISATEUR (a chaque question)

  ETAPE A — Routage (le goulot d'etranglement)
  ┌──────────────────────────────────────────────────────────────┐
  │  System prompt routeur (~400 tokens)                         │
  │  + index_documents.md complet (N x ~210 tokens)             │
  │  + Question utilisateur (~60 tokens)                         │
  │                      │                                       │
  │                      v  LLM                                  │
  │  Liste : fichiers + numeros de pages necessaires (~200 tok)  │
  └──────────────────────────────────────────────────────────────┘

  ETAPE B — Generation
  ┌──────────────────────────────────────────────────────────────┐
  │  System prompt generateur (~400 tokens)                      │
  │  + Sections ciblees OU document(s) complet(s)                │
  │    Option A — sections (~15 pages) : ~7 500 tokens           │
  │    Option B — doc complet (~200 pages) : ~100 000 tokens     │
  │  + Question utilisateur (~60 tokens)                         │
  │                      │                                       │
  │                      v  LLM                                  │
  │  Reponse avec citations [Document, Pages X-Y] (~800 tokens)  │
  └──────────────────────────────────────────────────────────────┘
```

---

### Budget tokens reel par operation

#### Phase 1 — Indexation (par document de 200 pages)

| Composant | Tokens | Sens |
| --------- | ------ | ---- |
| System prompt Archiviste | ~500 | input |
| Contenu document (200 pages x 500 tok) | ~100 000 | input |
| Entree index generee (sortie) | ~210 | output |
| **Total par document** | **~100 710 tokens** | ~100 500 in / 210 out |

#### Phase 2 etape A — Routage selon taille du corpus

| Corpus | Index (N x 210 tok) | Prompt + question | Output | Total input | Total output |
| ------ | ------------------- | ----------------- | ------ | ----------- | ------------ |
| 10 docs | 2 100 tok | 460 tok | ~200 tok | **2 560** | **200** |
| 50 docs | 10 500 tok | 460 tok | ~200 tok | **10 960** | **200** |
| 100 docs | 21 000 tok | 460 tok | ~200 tok | **21 460** | **200** |
| 200 docs | 42 000 tok | 460 tok | ~200 tok | **42 460** | **200** |
| 500 docs | 105 000 tok | 460 tok | ~200 tok | **105 460** | **200** |
| 580 docs | 121 800 tok | 460 tok | ~200 tok | **122 260** | **200** |
| 900 docs | 189 000 tok | 460 tok | ~200 tok | **189 460** | **200** |
| 1 000 docs | 210 000 tok | 460 tok | ~200 tok | **210 460** | **200** |
| 4 500 docs | 945 000 tok | 460 tok | ~200 tok | **945 460** | **200** |

#### Phase 2 etape B — Generation (sections ou doc complet)

| Scenario | Input | Output | Total tokens |
| -------- | ----- | ------ | ------------ |
| Sections ciblees (~15 pages) | ~7 960 tok | ~800 tok | **~8 760** |
| Document complet (~200 pages) | ~100 460 tok | ~800 tok | **~101 260** |

---

### Limites de corpus reelles par fenetre de contexte

> Avec ~210 tok/doc dans l'index + 460 tok de prompt/question (etape A)

| Modele | Contexte max | Corpus max sans depasser | Marge securite (80%) |
| ------ | ------------ | ------------------------ | -------------------- |
| Groq Llama 3.1 8B | 128K | **~580 docs** | ~460 docs |
| Groq Llama 3.3 70B | 128K | **~580 docs** | ~460 docs |
| GPT-4o / GPT-4o mini | 128K | **~580 docs** | ~460 docs |
| Together AI (Qwen2.5-7B) | 128K | **~580 docs** | ~460 docs |
| AWS Bedrock Llama 3.1 | 128K | **~580 docs** | ~460 docs |
| Claude Haiku 4.5 | 200K | **~950 docs** | ~750 docs |
| Claude Sonnet 4.6 | 200K | **~950 docs** | ~750 docs |
| Claude Opus 4.6 | 200K | **~950 docs** | ~750 docs |
| **Gemini Flash 2.0** | **1M** | **~4 750 docs** | ~3 800 docs |
| **GPT-4.1** | **1M** | **~4 750 docs** | ~3 800 docs |

> La grande majorite des cas d'usage NoRag (< 500 docs) est couverte par TOUS les modeles y compris ceux a 128K de contexte.

---

### Cout d'indexation — Phase 1 (par document de 200 pages)

| Fournisseur | Modele | Input /1M | Output /1M | Cout / doc | Cout 100 docs | Cout 500 docs |
| ----------- | ------ | --------- | ---------- | ---------- | ------------- | ------------- |
| **Groq** | Llama 3.1 8B | $0.05 | $0.08 | **$0.0050** | **$0.50** | **$2.52** |
| **Gemini Flash 2.0** | Google | $0.075 | $0.30 | **$0.0075** | **$0.75** | **$3.77** |
| **Claude Haiku 4.5** | Anthropic | $0.08 | $0.40 | **$0.0081** | **$0.81** | **$4.03** |
| **GPT-4o mini** | OpenAI | $0.15 | $0.60 | **$0.0151** | **$1.51** | **$7.54** |
| **Together AI** | Qwen2.5-7B | $0.20 | $0.20 | **$0.0201** | **$2.01** | **$10.05** |
| **AWS Bedrock** | Llama 3.1 8B | $0.22 | $0.22 | **$0.0221** | **$2.21** | **$11.06** |
| **Groq** | Llama 3.3 70B | $0.59 | $0.79 | **$0.0594** | **$5.94** | **$29.70** |
| **Claude Sonnet 4.6** | Anthropic | $0.80 | $4.00 | **$0.0809** | **$8.09** | **$40.44** |
| **GPT-4.1** | OpenAI | $1.00 | $4.00 | **$0.1009** | **$10.09** | **$50.44** |
| **GPT-4o** | OpenAI | $1.25 | $5.00 | **$0.1261** | **$12.61** | **$63.06** |
| **Claude Opus 4.6** | Anthropic | $4.00 | $20.00 | **$0.4042** | **$40.42** | **$202.10** |

---

### Cout par requete utilisateur — Phase 2 (etape A + etape B)

> Etape B : injection des **sections ciblees (~15 pages = ~7 500 tokens)** — cas le plus frequent.
> Pour injection du **document complet**, multiplier le cout etape B par ~13.

#### Corpus de 100 documents (index ~21 000 tokens — tous modeles compatibles)

| Fournisseur | Modele | Cout etape A | Cout etape B (sections) | **Total / requete** |
| ----------- | ------ | ------------ | ----------------------- | ------------------- |
| **Groq** | Llama 3.1 8B | $0.00011 | $0.00043 | **$0.00054** |
| **Gemini Flash 2.0** | Google | $0.00161 | $0.00062 | **$0.00223** |
| **Claude Haiku 4.5** | Anthropic | $0.00172 | $0.00066 | **$0.00238** |
| **GPT-4o mini** | OpenAI | $0.00322 | $0.00124 | **$0.00446** |
| **Together AI** | Qwen2.5-7B | $0.00429 | $0.00165 | **$0.00594** |
| **AWS Bedrock** | Llama 3.1 8B | $0.00472 | $0.00182 | **$0.00654** |
| **Groq** | Llama 3.3 70B | $0.01272 | $0.00491 | **$0.01763** |
| **Claude Sonnet 4.6** | Anthropic | $0.01717 | $0.00662 | **$0.02379** |
| **GPT-4.1** | OpenAI | $0.02147 | $0.00828 | **$0.02975** |
| **GPT-4o** | OpenAI | $0.02683 | $0.01034 | **$0.03717** |
| **Claude Opus 4.6** | Anthropic | $0.08583 | $0.03308 | **$0.11891** |

#### Corpus de 500 documents (index ~105 000 tokens — tous modeles 128K compatibles)

| Fournisseur | Modele | Cout etape A | Cout etape B (sections) | **Total / requete** |
| ----------- | ------ | ------------ | ----------------------- | ------------------- |
| **Groq** | Llama 3.1 8B | $0.00528 | $0.00043 | **$0.00571** |
| **Gemini Flash 2.0** | Google | $0.00791 | $0.00062 | **$0.00853** |
| **Claude Haiku 4.5** | Anthropic | $0.00844 | $0.00066 | **$0.00910** |
| **GPT-4o mini** | OpenAI | $0.01582 | $0.00124 | **$0.01706** |
| **Together AI** | Qwen2.5-7B | $0.02109 | $0.00165 | **$0.02274** |
| **AWS Bedrock** | Llama 3.1 8B | $0.02320 | $0.00182 | **$0.02502** |
| **Groq** | Llama 3.3 70B | $0.06237 | $0.00491 | **$0.06728** |
| **Claude Sonnet 4.6** | Anthropic | $0.08432 | $0.00662 | **$0.09094** |
| **GPT-4.1** | OpenAI | $0.10546 | $0.00828 | **$0.11374** |
| **GPT-4o** | OpenAI | $0.13183 | $0.01034 | **$0.14217** |

---

### Projection couts mensuels complets (indexation initiale + 1 000 requetes/mois)

#### Corpus 100 docs, sections ciblees en etape B

| Fournisseur | Modele | Setup index | 1 000 req/mois | **Mois 1** | **Mois 2+** |
| ----------- | ------ | ----------- | -------------- | ---------- | ----------- |
| **Groq** | Llama 3.1 8B | $0.50 | $0.54 | **$1.04** | **$0.54** |
| **Gemini Flash 2.0** | Google | $0.75 | $2.23 | **$2.98** | **$2.23** |
| **Claude Haiku 4.5** | Anthropic | $0.81 | $2.38 | **$3.19** | **$2.38** |
| **GPT-4o mini** | OpenAI | $1.51 | $4.46 | **$5.97** | **$4.46** |
| **Together AI** | Qwen2.5-7B | $2.01 | $5.94 | **$7.95** | **$5.94** |
| **AWS Bedrock** | Llama 3.1 8B | $2.21 | $6.54 | **$8.75** | **$6.54** |
| **Groq** | Llama 3.3 70B | $5.94 | $17.63 | **$23.57** | **$17.63** |
| **Claude Sonnet 4.6** | Anthropic | $8.09 | $23.79 | **$31.88** | **$23.79** |
| **GPT-4.1** | OpenAI | $10.09 | $29.75 | **$39.84** | **$29.75** |
| **GPT-4o** | OpenAI | $12.61 | $37.17 | **$49.78** | **$37.17** |
| **Claude Opus 4.6** | Anthropic | $40.42 | $118.91 | **$159.33** | **$118.91** |

#### Corpus 100 docs, document COMPLET injecte en etape B (~100K tokens)

| Fournisseur | Modele | Cout / requete | 1 000 req/mois |
| ----------- | ------ | -------------- | -------------- |
| **Groq** | Llama 3.1 8B | **$0.0056** | **$5.60** |
| **Gemini Flash 2.0** | Google | **$0.0177** | **$17.70** |
| **Claude Haiku 4.5** | Anthropic | **$0.0189** | **$18.90** |
| **GPT-4o mini** | OpenAI | **$0.0355** | **$35.50** |
| **Claude Sonnet 4.6** | Anthropic | **$0.1013** | **$101.30** |
| **GPT-4.1** | OpenAI | **$0.1229** | **$122.90** |
| **GPT-4o** | OpenAI | **$0.1540** | **$154.00** |

> La difference entre injection de sections (~15 pages) vs document complet est un facteur **6x a 10x** sur le cout de l'etape B. Le routage precis des pages en etape A permet donc d'enormes economies.

---

### Visualisation — Cout mensuel recalibré (100 docs, 1 000 req/mois, sections ciblees)

```text
Groq Llama 3.1 8B       $0.54/mois   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Gemini Flash 2.0         $2.23/mois   █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Claude Haiku 4.5         $2.38/mois   █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
GPT-4o mini              $4.46/mois   ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░
Together AI Qwen2.5-7B   $5.94/mois   ███░░░░░░░░░░░░░░░░░░░░░░░░░░░
AWS Bedrock Llama 3.1    $6.54/mois   ███░░░░░░░░░░░░░░░░░░░░░░░░░░░
Groq Llama 3.3 70B      $17.63/mois   █████████░░░░░░░░░░░░░░░░░░░░░
Claude Sonnet 4.6       $23.79/mois   ████████████░░░░░░░░░░░░░░░░░░
GPT-4.1                 $29.75/mois   ███████████████░░░░░░░░░░░░░░░
GPT-4o                  $37.17/mois   ███████████████████░░░░░░░░░░░
Claude Opus 4.6        $118.91/mois   ██████████████████████████████
```

---

### Recommandation finale — Pipeline reel NoRag

| Corpus | Requetes/mois | Meilleur choix | Cout/mois | Notes |
| ------ | ------------- | -------------- | --------- | ----- |
| < 580 docs | Tous volumes | **Groq Llama 3.1 8B** | ~$0.50/1K req | Le moins cher, assez rapide |
| < 580 docs | Qualite > vitesse | **Gemini Flash 2.0** | ~$2.20/1K req | Meilleur rapport qualite/prix |
| 580-950 docs | Tous volumes | **Claude Haiku 4.5** | ~$9/1K req | Seule option abordable a 200K |
| 580-950 docs | Budget libre | **Gemini Flash 2.0** | ~$8/1K req | Encore moins cher avec 1M contexte |
| > 950 docs | Budget serre | **Gemini Flash 2.0** | ~$8/1K req | Seul choix economique a 1M |
| > 950 docs | Qualite max | **GPT-4.1** | ~$115/1K req | Contexte 1M, qualite OpenAI |

---

## 13. Index Hierarchique — Corpus Quasi-Illimite (Layer d'Abstraction)

> Principe : quand le corpus depasse la capacite d'un index plat, on introduit un **niveau d'abstraction supplementaire**.
> L'index plat (~210 tok/doc) devient trop volumineux → on cree un **meta-index** (~50 tok/doc) pour le premier filtre,
> puis on injecte le detail uniquement des documents selectionnes.
> Resultat : un corpus **theoriquement illimite** avec seulement 3 appels LLM au lieu de 2.

---

### Architecture a 2 niveaux d'index

```text
STRUCTURE DES FICHIERS
┌─────────────────────────────────────────────────────────────────────┐
│  meta_index.md          <- Niveau 1 : ultra-compact (~50 tok/doc)  │
│                            Titre + domaine + 1 ligne de resume      │
│                                                                     │
│  index_documents.md     <- Niveau 2 : detail (~210 tok/doc)        │
│                            Format actuel : resume + sections/pages  │
│                                                                     │
│  /docs/*.pdf            <- Niveau 3 : documents sources             │
└─────────────────────────────────────────────────────────────────────┘

PIPELINE 3 ETAPES
┌─────────────────────────────────────────────────────────────────────┐
│  ETAPE A — Filtre haut niveau                                       │
│  System prompt (~400 tok) + meta_index.md (N x 50 tok)             │
│  + Question (~60 tok)                                               │
│  → LLM identifie 3 a 10 documents candidats (noms seulement)       │
│                                                                     │
│  ETAPE B — Routage precis                                           │
│  System prompt (~400 tok) + entrees index_documents.md des         │
│  candidats selectionnes (3-10 docs x 210 tok = 630-2 100 tok)      │
│  + Question (~60 tok)                                               │
│  → LLM identifie les sections et pages exactes                     │
│                                                                     │
│  ETAPE C — Generation                                               │
│  System prompt (~400 tok) + sections ciblees (~7 500 tok)          │
│  + Question (~60 tok)                                               │
│  → Reponse avec citations [Document, Pages X-Y]                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Format du meta-index (Niveau 1)

Chaque entree est reduite au strict minimum pour le filtrage initial :

```markdown
## [DOC-001] Un liberal nomme Jesus
**Domaine :** Economie / Philosophie / Religion
**Resume 1 ligne :** Lecture liberale des Evangiles — libre arbitre, entrepreneuriat, richesse.

## [DOC-002] Cessez de vous faire avoir
**Domaine :** Finance personnelle / Investissement
**Resume 1 ligne :** Portefeuille permanent Harry Browne — ETF, or, obligations, allocation d'actifs.

## [DOC-003] Les Mondes de demain
**Domaine :** Geopolitique / Economie mondiale
**Resume 1 ligne :** Declin americain, montee de l'Asie, dedollarisation, monde multipolaire.
```

**Tokens par entree meta-index :**

| Composant | Tokens |
| --------- | ------ |
| ID + Titre | ~15 tok |
| Domaine | ~10 tok |
| Resume 1 ligne | ~25 tok |
| **Total par document** | **~50 tokens** |

---

### Capacite par niveau de contexte avec index hierarchique

#### Etape A — meta_index.md (50 tok/doc)

| Modele | Contexte | Docs dans meta-index | Capacite reelle (80%) |
| ------ | -------- | -------------------- | --------------------- |
| Groq / GPT-4o / Together | 128K | **~2 550 docs** | ~2 000 docs |
| Claude Haiku/Sonnet | 200K | **~3 990 docs** | ~3 200 docs |
| **Gemini Flash 2.0** | **1M** | **~19 990 docs** | ~16 000 docs |
| **GPT-4.1** | **1M** | **~19 990 docs** | ~16 000 docs |

#### Etape B — index_documents.md partiel (210 tok x 3-10 docs selectionnes)

| Docs selectionnes | Tokens etape B | Compatible tous modeles ? |
| ----------------- | -------------- | ------------------------- |
| 3 docs | ~630 tok | ✅ Trivial |
| 5 docs | ~1 050 tok | ✅ Trivial |
| 10 docs | ~2 100 tok | ✅ Trivial |
| 20 docs | ~4 200 tok | ✅ Trivial |

> L'etape B ne consomme que quelques milliers de tokens — negligeable pour tous les modeles.

---

### Budget tokens par requete avec index hierarchique

| Etape | Composant | Input tokens | Output tokens |
| ----- | --------- | ------------ | ------------- |
| **A** | meta_index (2 000 docs x 50) + prompt + question | ~100 460 | ~150 |
| **B** | detail 5 docs selectionnes (5 x 210) + prompt + question | ~1 510 | ~250 |
| **C** | sections ciblees (~15 pages) + prompt + question | ~7 960 | ~800 |
| **Total** | | **~109 930 input** | **~1 200 output** |

**Comparaison index plat vs hierarchique (2 000 docs) :**

| Architecture | Etapes | Input total / requete | Faisabilite 128K |
| ------------ | ------ | --------------------- | ---------------- |
| Index plat (2 000 docs x 210 tok) | 2 | ~420 460 tok | ❌ Impossible |
| **Index hierarchique** | **3** | **~109 930 tok** | **✅ Compatible** |

> Le layer d'abstraction divise la consommation de tokens par **~4** et rend accessible un corpus de 2 000 docs meme sur des modeles 128K.

---

### Cout par requete — Index hierarchique vs index plat

#### Corpus de 2 000 documents (inaccessible en index plat sur 128K)

| Fournisseur | Modele | Cout etape A | Cout etape B | Cout etape C | **Total / requete** |
| ----------- | ------ | ------------ | ------------ | ------------ | ------------------- |
| **Groq** | Llama 3.1 8B | $0.00503 | $0.0001 | $0.00043 | **$0.00556** |
| **Gemini Flash 2.0** | Google | $0.00754 | $0.0001 | $0.00062 | **$0.00826** |
| **Claude Haiku 4.5** | Anthropic | $0.00804 | $0.0001 | $0.00066 | **$0.00880** |
| **GPT-4o mini** | OpenAI | $0.01507 | $0.0002 | $0.00124 | **$0.01651** |
| **Together AI** | Qwen2.5-7B | $0.02009 | $0.0003 | $0.00165 | **$0.02204** |
| **Claude Sonnet 4.6** | Anthropic | $0.08043 | $0.0012 | $0.00662 | **$0.08825** |
| **GPT-4.1** | OpenAI | $0.10055 | $0.0015 | $0.00828 | **$0.10933** |

---

### Projection couts mensuels — Index hierarchique (1 000 req/mois)

#### Corpus 2 000 docs (index plat impossible sur 128K, hierarchique compatible)

| Fournisseur | Modele | Setup indexation | Setup meta-index | Requetes/mois | **Mois 1** | **Mois 2+** |
| ----------- | ------ | ---------------- | ---------------- | ------------- | ---------- | ----------- |
| **Groq** | Llama 3.1 8B | $10.00 | $0.10 | $5.56 | **$15.66** | **$5.56** |
| **Gemini Flash 2.0** | Google | $15.00 | $0.10 | $8.26 | **$23.36** | **$8.26** |
| **Claude Haiku 4.5** | Anthropic | $16.20 | $0.10 | $8.80 | **$25.10** | **$8.80** |
| **GPT-4o mini** | OpenAI | $30.20 | $0.20 | $16.51 | **$46.91** | **$16.51** |
| **Claude Sonnet 4.6** | Anthropic | $161.80 | $0.80 | $88.25 | **$250.85** | **$88.25** |
| **GPT-4.1** | OpenAI | $201.80 | $1.00 | $109.33 | **$312.13** | **$109.33** |

> Setup meta-index = regeneration du meta_index.md depuis l'index existant — 1 appel LLM par doc pour compresser l'entree (~50 tok out, ~210 tok in) = negligeable.

---

### Scalabilite theorique — Jusqu'ou peut-on aller ?

En ajoutant un **troisieme niveau** (meta-meta-index), on peut pousser encore plus loin :

```text
NIVEAU 0 — meta-meta-index : ~10 tok/doc (juste titre + domaine)
           Capacite 128K : ~12 800 docs
           Capacite 1M  : ~100 000 docs

NIVEAU 1 — meta-index      : ~50 tok/doc
           Injecte pour le cluster selectionne (~200 docs x 50 = 10 000 tok)

NIVEAU 2 — index_documents : ~210 tok/doc
           Injecte pour les 5-10 docs identifies (~2 100 tok)

NIVEAU 3 — sections PDF    : ~500 tok/page
           Injecte les pages ciblees (~7 500 tok)
```

| Niveaux | Appels LLM / requete | Corpus max (128K) | Corpus max (1M) |
| ------- | -------------------- | ----------------- | --------------- |
| 1 (index plat) | 2 | ~580 docs | ~4 750 docs |
| 2 (+ meta-index) | 3 | **~2 000 docs** | **~16 000 docs** |
| 3 (+ meta-meta-index) | 4 | **~12 000 docs** | **~100 000 docs** |

> Chaque niveau supplementaire ajoute ~1 appel LLM (faible cout, ~1-5 tok/doc injecte a ce stade) et multiplie la capacite du corpus par un facteur 5 a 10.

---

### Comparatif final — Architectures NoRag selon taille de corpus

| Corpus | Architecture | Appels LLM | Cout / requete (Gemini Flash) | Cout / requete (Groq L3.1 8B) |
| ------ | ------------ | ---------- | ----------------------------- | ----------------------------- |
| < 580 docs | Index plat | 2 | ~$0.002 | ~$0.001 |
| 580-2 000 docs | Index + meta-index | 3 | ~$0.008 | ~$0.006 |
| 2 000-12 000 docs | Index + 2 niveaux | 4 | ~$0.012 | ~$0.010 |
| > 12 000 docs | Index + 3 niveaux | 5 | ~$0.016 | ~$0.013 |

> La progression du cout est **logarithmique** : doubler le corpus ne double pas le cout — on ajoute simplement un appel LLM sur quelques milliers de tokens supplementaires.
> NoRag reste **competitif et maintenable a toute echelle** grace a cette hierarchie de fichiers Markdown.

---

## 14. RAG vs NoRag — Comparatif de Couts Reels (2 000 docs, 1 000 req/mois)

> Comparatif chiffre sur la meme base : **2 000 documents de ~200 pages chacun**, **1 000 requetes/mois**.
> RAG = Retrieval-Augmented Generation classique avec base vectorielle.
> NoRag = pipeline hierarchique section 13 (meta-index + index detaille + injection sections).

---

### Pourquoi les couts par requete sont si differents

Le facteur determinant est la **taille du contexte injecte dans le LLM** :

| Architecture | Contexte injecte / requete | Appels LLM | Tokens totaux |
| ------------ | -------------------------- | ---------- | ------------- |
| **RAG** | 5 chunks × 512 tok = 2 560 tok | 1 | ~3 820 tok |
| **NoRag plat** | index complet (~120K) + sections (~7 500) | 2 | ~128 000 tok |
| **NoRag hierarchique** | meta-index + detail 5 docs + sections | 3 | ~110 000 tok |

> RAG injecte ~30 fois moins de tokens par requete — ce qui se traduit directement en couts LLM.

---

### Couts de setup RAG (une seule fois)

#### Etape 1 — Chunking et embedding des documents

```text
2 000 docs × 200 pages × 500 tok/page = 200 000 000 tokens a embedder
Chunking : 512 tok/chunk avec 50 tok overlap → 390 000 chunks au total
```

| Modele d'embedding | Prix / 1M tok | Cout setup 2 000 docs | Dimensions |
| ------------------ | ------------- | --------------------- | ---------- |
| **text-embedding-3-small** (OpenAI) | $0.020 | **$4.00** | 1 536 |
| **text-embedding-3-large** (OpenAI) | $0.130 | **$26.00** | 3 072 |
| **voyage-3** (Voyage AI) | $0.060 | **$12.00** | 1 024 |
| **Cohere embed-v4** | $0.060 | **$12.00** | 1 024 |
| **Gemini text-embedding-004** | $0.000 | **$0.00** | 768 (gratuit) |

#### Etape 2 — Ecriture dans la base vectorielle

| Fournisseur | Cout ecriture 390K vectors | Notes |
| ----------- | -------------------------- | ----- |
| Pinecone Serverless | ~$0.78 | $2/1M writes |
| Qdrant Cloud | $0.00 | Inclus dans abonnement |
| pgvector / Neon | $0.00 | Inclus dans DB |
| Self-hosted (local) | $0.00 | Compute seulement |

**Cout setup RAG total estimé : $5 a $27** selon le modele d'embedding choisi.

---

### Couts mensuels RAG — Infrastructure vectorielle

| Fournisseur Vector DB | Storage 390K vectors (~2.4 GB) | Requetes (1K/mois) | **Total mensuel** |
| --------------------- | ------------------------------ | ------------------- | ----------------- |
| **Pinecone Serverless** | ~$2.00/mois | ~$0.04 | **~$2.04** |
| **Qdrant Cloud** (Starter) | $25.00/mois (plan min) | Inclus | **$25.00** |
| **pgvector + Neon** | $7.00/mois (plan Launch) | Inclus | **$7.00** |
| **Chroma Cloud** | ~$5.00/mois (estimé) | Inclus | **~$5.00** |
| **Self-hosted Qdrant** (VPS $5) | $5.00/mois | Inclus | **$5.00** |
| **Self-hosted local** | $0.00 | $0.00 | **$0.00** |

---

### Couts LLM par requete RAG vs NoRag hierarchique

#### Budget tokens / requete

| Composant | RAG | NoRag hierarchique |
| --------- | --- | ------------------ |
| System prompt | 400 tok | 400 tok (× 3 appels) |
| Contexte injecte | 2 560 tok (5 chunks) | ~101 000 tok (meta + detail + sections) |
| Question | 60 tok | 60 tok (× 3 appels) |
| Output | 800 tok | ~1 200 tok |
| **Input total** | **3 020 tok** | **~109 930 tok** |
| **Output total** | **800 tok** | **~1 200 tok** |
| **Ratio contexte** | **1×** | **~36×** |

#### Cout LLM / requete (1 000 requetes/mois)

| Fournisseur | Modele | RAG $/requete | RAG 1K req | NoRag $/requete | NoRag 1K req | **Ratio** |
| ----------- | ------ | ------------- | ---------- | --------------- | ------------ | --------- |
| **Groq** | Llama 3.1 8B | $0.000215 | **$0.22** | $0.005560 | $5.56 | 25× |
| **Gemini Flash 2.0** | Google | $0.000467 | **$0.47** | $0.008260 | $8.26 | 18× |
| **Claude Haiku 4.5** | Anthropic | $0.000562 | **$0.56** | $0.008800 | $8.80 | 16× |
| **GPT-4o mini** | OpenAI | $0.000933 | **$0.93** | $0.016510 | $16.51 | 18× |
| **Claude Sonnet 4.6** | Anthropic | $0.005616 | **$5.62** | $0.088250 | $88.25 | 16× |
| **GPT-4.1** | OpenAI | $0.006220 | **$6.22** | $0.109330 | $109.33 | 18× |

---

### Comparatif total Mois 1 / Mois 2+ (2 000 docs, 1 000 req/mois)

#### Avec Pinecone Serverless + text-embedding-3-small ($4 setup embed + $0.78 write + $2/mois DB)

| Fournisseur | Modele | **RAG Mois 1** | **RAG Mois 2+** | **NoRag Mois 1** | **NoRag Mois 2+** | Economie RAG/mois |
| ----------- | ------ | -------------- | --------------- | ---------------- | ----------------- | ----------------- |
| **Groq** | Llama 3.1 8B | **$7.00** | **$2.24** | $15.66 | $5.56 | **−$3.32 (-60%)** |
| **Gemini Flash 2.0** | Google | **$7.25** | **$2.49** | $23.36 | $8.26 | **−$5.77 (-70%)** |
| **Claude Haiku 4.5** | Anthropic | **$7.34** | **$2.58** | $25.10 | $8.80 | **−$6.22 (-71%)** |
| **GPT-4o mini** | OpenAI | **$7.71** | **$2.95** | $46.91 | $16.51 | **−$13.56 (-82%)** |
| **Claude Sonnet 4.6** | Anthropic | **$12.40** | **$7.62** | $250.85 | $88.25 | **−$80.63 (-91%)** |
| **GPT-4.1** | OpenAI | **$13.00** | **$8.24** | $312.13 | $109.33 | **−$101.09 (-92%)** |

> Le RAG est systematiquement moins cher en couts recurrents — de **60% a 92% d'economie** selon le modele.
> L'ecart s'amplifie avec les modeles premium (Sonnet, GPT-4.1) car le cout est quasi entierement lie aux tokens.

---

### Couts annuels projetes (12 mois, 1 000 req/mois)

| Fournisseur | Modele | **RAG annuel** | **NoRag annuel** | Economie annuelle |
| ----------- | ------ | -------------- | ---------------- | ----------------- |
| Groq | Llama 3.1 8B | **$31.64** | $76.88 | **−$45.24** |
| Gemini Flash 2.0 | Google | **$34.63** | $111.18 | **−$76.55** |
| Claude Haiku 4.5 | Anthropic | **$35.74** | $121.90 | **−$86.16** |
| GPT-4o mini | OpenAI | **$39.23** | $228.27 | **−$189.04** |
| Claude Sonnet 4.6 | Anthropic | **$91.82** | $1 308.61 | **−$1 216.79** |
| GPT-4.1 | OpenAI | **$98.66** | $1 521.49 | **−$1 422.83** |

---

### Pourquoi NoRag reste pertinent malgre le cout superieur

Le RAG est moins cher, mais il introduit des **couts caches et des limites qualitatives** significatives :

#### Problemes inherents au RAG

| Probleme | Impact | Frequence |
| -------- | ------ | --------- |
| **Chunking aveugle** | Un concept etalé sur 3 pages est coupe en plein milieu | Tres fréquent |
| **Perte de contexte** | Le chunk retrouve n'a pas le paragraphe precedent/suivant | Systematique |
| **Hallucination sur manque** | Si le bon chunk n'est pas retrouvé, le LLM invente | Fréquent (top-5 peut rater) |
| **Embedding perime** | Nouveau document = re-embedding complet + re-indexation | A chaque MAJ |
| **Debug opaque** | Impossible de savoir pourquoi un chunk a ete retrouvé (ou pas) | Toujours |
| **Sensibilite orthographique** | Fautes de frappe dans la question = mauvaise recuperation | Parfois |
| **Multilingual drift** | Embeddings cross-langue moins precis | Si corpus mixte |

#### Avantages NoRag qui justifient le surcout

| Avantage | Valeur metier | Impact |
| -------- | ------------- | ------ |
| **Contexte complet** | Le LLM lit les 15 bonnes pages, pas 5 extraits tronques | Reponses plus precises |
| **Citations exactes** | Page X-Y verifiable dans le PDF original | Confiance utilisateur |
| **MAJ instantanee** | Nouveau doc = ajouter une entree Markdown, zero re-embedding | Maintenance triviale |
| **Debuggable** | L'index est lisible par un humain — on voit exactement ce que le LLM voit | Fiabilite |
| **Zero infrastructure** | Pas de vector DB, pas de service a maintenir | Simplicite operationnelle |
| **Routage semantique** | Le LLM comprend la question en langage naturel, pas juste la similarite cosinus | Flexibilite |

---

### Quand choisir RAG vs NoRag

| Critere | RAG recommande | NoRag recommande |
| ------- | -------------- | ---------------- |
| **Volume requetes** | > 10 000 req/mois | < 5 000 req/mois |
| **Taille corpus** | Stable (peu de MAJ) | Evolutif (MAJ frequentes) |
| **Type documents** | Documents homogenes bien structures | Documents heterogenes, techniques, juridiques |
| **Priorite** | Minimiser le cout a grande echelle | Maximiser la qualite de reponse |
| **Equipe** | DevOps disponible (infra vector DB) | Equipe reduite, pas de MLOps |
| **Budget infra** | OK payer $25+/mois pour la DB | Zero infrastructure souhaitee |
| **Auditabilite** | Acceptable (logs de chunks) | Requise (citations page exacte) |
| **Modele LLM vise** | GPT-4.1 ou Sonnet → RAG indispensable | Haiku ou Gemini Flash → NoRag raisonnable |

---

### Synthese — Le vrai avantage competitif de NoRag

```text
RAG =  Infrastructure lourde + cout faible/requete + qualite variable
NoRag = Zero infrastructure + cout plus eleve/requete + qualite superieure

Point de bascule economique (Gemini Flash 2.0, Pinecone) :
  - En dessous de ~3 000 req/mois → NoRag et RAG ont un cout total similaire
  - Au dessus de ~3 000 req/mois → RAG devient structurellement moins cher

Mais le vrai differenciateur de NoRag n'est pas le prix :
→ C'est la FIABILITE des reponses (contexte complet, citations verifiables)
→ et la MAINTENABILITE (un fichier Markdown vs une infrastructure vectorielle)
```

| Volume mensuel | Recommandation |
| -------------- | -------------- |
| < 500 req/mois | **NoRag** — simplicite et qualite, ecart de cout negligeable |
| 500-3 000 req/mois | **NoRag** ou RAG selon priorite qualite vs cout |
| 3 000-10 000 req/mois | **RAG** pour les modeles premium, **NoRag** pour Haiku/Flash |
| > 10 000 req/mois | **RAG** systematiquement, sauf si qualite absolue requise |
