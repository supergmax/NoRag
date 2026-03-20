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
