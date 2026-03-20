# NoRag v2 — 3-Index Document System (Multi-LLM)

NoRag v2 is a **Document Q&A** system that replaces vector embeddings (traditional RAG) with **100% LLM-based routing using 3 Markdown Index Files**.

It leverages the **massive context windows** of modern models (Gemini Flash, Claude 3.5, GPT-4o, Grok) to analyze, route, and extract precise answers with mandatory citations.

---

## 🏗️ Architecture: The 3-Step Pipeline

Instead of chunking texts into opaque vectors, NoRag maintains **3 clear-text Markdown Indexes** in the `data/` folder:
1. `index_agents.md`: Available agents and their roles.
2. `index_documents.md`: The document catalog and their sections (with keywords).
3. `index_history.md`: Summary of past sessions.

**The Pipeline:**
1. **Step 1 — ROUTING (silent)**: The LLM reads `index_documents.md` + the user's question. It identifies 1 to 3 relevant documents/sections.
2. **Step 2 — CONTEXT**: The system reads conversation summaries from `index_history.md` to maintain continuity.
3. **Step 3 — GENERATION**: Retrieves the targeted text (from a PDF, the database, or directly by the agent) and generates the answer. **Mandatory citations: `[Document, Pages X-Y]`**.

---

## 🚀 Global Installation

Regardless of how you use it, clone the repo and install the prerequisites:

```bash
git clone https://github.com/your-username/NoRag.git
cd NoRag
pip install -r requirements.txt
cp .env.example .env
```

In `.env`, you must add your Gemini Key (used by the API for routing and generation):
```env
GEMINI_API_KEY=AIzaSy...
```

---

## 🛠️ Usage Modes

NoRag is designed to be highly flexible. You can use it:
- **A. Without API / No Code**: Directly within your favorite LLM's web chat.
- **B. Interactive Local (CLI)**: A terminal with SQLite history.
- **C. REST API (SQLite)**: Standalone local server.
- **D. REST API (Supabase)**: Cloud database for deployments.

### Mode A: As an Autonomous Agent (No API, No DB)

Don't want to run a server? You can use NoRag directly in **ChatGPT**, **Claude**, **Gemini**, **Grok**, or an IDE like **Antigravity**.

1. Open the `norag/plugins/` folder.
2. Open the file corresponding to your AI (e.g., `gpt_instructions.md`).
3. Copy the **System Prompt** and paste it into the AI's custom instructions.
4. In your first message to the AI, send the content of the 3 files located in `data/` (`index_agents.md`, `index_documents.md`, `index_history.md`).
5. **That's it!** The AI will adopt the NoRag behavior.

*Note for Claude Code (Terminal)*: Copy `norag/plugins/claude_skill.md` into your Claude skills to enable direct reading of local PDFs without any API.

---

### Mode B: Local Interactive CLI (With SQLite history)

Fast interactive terminal mode. It uses the local SQLite database (`norag.db`) to save sessions.

```bash
python -m api.local_query
```

> **Example session:**
> You > What does Charles Gave say about inflation?
> NoRag > According to [Les Mondes de demain, Pages 41-84], inflation...

Available commands: `/list`, `/archive`, `/quit`.

---

### Mode C: Full REST API (Local SQLite Backend)

Runs a web server that manages requests, history, and indexing. No complex setup: an SQLite database (`local/norag.db`) is automatically created upon startup.

**Recommended `.env` configuration:**
```env
NORAG_BACKEND=sqlite
SQLITE_DB_PATH=local/norag.db
GEMINI_API_KEY=AIza...
```

**Startup:**
```bash
uvicorn api.main:app --reload
```

- The API runs on: `http://localhost:8000`
- Swagger / Interactive documentation: `http://localhost:8000/docs`

You will find the endpoints `/index/`, `/query/`, `/documents/`, `/archive/`.

---

### Mode D: Cloud REST API (Supabase PostgreSQL Backend)

Ideal for deploying NoRag in production on a VPS or Vercel. History, documents, and index cache are stored in the Cloud on Supabase.

#### 1. Supabase Setup
1. Create a project on [supabase.com](https://supabase.com).
2. Go to the **SQL Editor**, create a new query, and run the following script to generate the tables:

```sql
-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY, titre TEXT NOT NULL,
    resume_global TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);

-- Chunks table (Sections)
CREATE TABLE IF NOT EXISTS chunks_documents (
    id SERIAL PRIMARY KEY, document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    titre_section TEXT NOT NULL, mots_cles TEXT NOT NULL,
    contenu_complet TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);

-- History table (Sessions)
CREATE TABLE IF NOT EXISTS memoire_norag (
    id SERIAL PRIMARY KEY, session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    contenu TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON memoire_norag (session_id, cree_le DESC);
```

#### 2. `.env` Configuration
Get your credentials in Supabase (Project Settings -> API):

```env
NORAG_BACKEND=supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1...
GEMINI_API_KEY=AIza...
```

#### 3. Startup
```bash
uvicorn api.main:app --reload
```
The API will automatically point to your online database.

---

## 📚 Workflow: How to add a new document?

The goal is to populate `data/index_documents.md` and Optionally the database.

If you use the **Database mode (Mode C or D)**:
1. Start the API (`uvicorn api.main:app`).
2. Copy the raw text of your PDF chapter/document.
3. Use the `POST /archive` endpoint (via Swagger or curl) by sending this text. The "Archiviste" AI will structure the document with summaries and keywords.
4. Inject the archivist's response into the database with the `POST /documents` endpoint.
5. Use `POST /index/rebuild` to regenerate the `index_documents.md` file on the hard drive.

If you use the **Autonomous Agent mode (Mode A)**:
1. Simply ask the AI: `/archive [paste your PDF content here]`.
2. The AI will reply with a structured card.
3. Copy-paste this card directly into the `data/index_documents.md` file.

---

## 🧱 v2 Project Structure

```text
NoRag/
├── core/                  # Main engine (Indexer, config, storage, index_builder)
├── data/                  # Your documents and Clear-text Indexes
│   ├── index_agents.md    # -> List of skills
│   ├── index_documents.md # -> Keywords for Routing
│   └── index_history.md   # -> Conversation summaries
├── api/                   # FastAPI interface (REST server)
├── norag/                 # LLM Utilities
│   └── plugins/           # -> Copyable prompts for Claude, GPT, Gemini, Grok
└── README.md
```

---
---

# NoRag v2 — Système Documentaire à 3 Index (FR)

NoRag v2 est un système de **Questions/Réponses documentaire (Q&A)** qui remplace les embeddings vectoriels (RAG traditionnel) par un **routage 100% LLM basé sur 3 Fichiers Index Markdown**. 

Il tire parti des **très grandes fenêtres de contexte** des modèles modernes (Gemini Flash, Claude 3.5, GPT-4o, Grok) pour analyser, router, et extraire des réponses précises avec citations obligatoires.

---

## 🏗️ Architecture : Le Pipeline en 3 Étapes

Au lieu de découper les textes en vecteurs opaques, NoRag maintient **3 Index en texte clair (Markdown)** dans le dossier `data/` :
1. `index_agents.md` : Les agents disponibles et leurs rôles.
2. `index_documents.md` : Le catalogue des documents et leurs sections (avec mots-clés).
3. `index_history.md` : Le résumé des sessions passées.

**Le Pipeline :**
1. **Étape 1 — ROUTAGE (silencieux)** : Le LLM lit `index_documents.md` + la question de l'utilisateur. Il identifie 1 à 3 documents/sections pertinents.
2. **Étape 2 — CONTEXTE** : Le système lit les résumés des conversations depuis `index_history.md` pour maintenir la continuité.
3. **Étape 3 — GÉNÉRATION** : Récupération du texte ciblé (depuis un PDF, la base de données, ou directement par l'agent) et génération de la réponse. **Citations obligatoires : `[Document, Pages X-Y]`**.

---

## 🚀 Installation Globale

Peu importe le mode d'utilisation, clonez le repo et installez les prérequis :

```bash
git clone https://github.com/votre-user/NoRag.git
cd NoRag
pip install -r requirements.txt
cp .env.example .env
```

Dans `.env`, ajoutez impérativement votre clé Gemini (utilisée par l'API pour router et générer) :
```env
GEMINI_API_KEY=AIzaSy...
```

---

## 🛠️ Modes d'Utilisation

NoRag est conçu pour être hyper-flexible. Vous pouvez l'utiliser :
- **A. Sans API / Sans Code** : Directement dans le chat web de votre LLM préféré.
- **B. En Local interactif (CLI)** : Un terminal avec historique SQLite.
- **C. En API REST (SQLite)** : Serveur local autonome.
- **D. En API REST (Supabase)** : Base de données Cloud pour déploiements.

### Mode A : En Agent Autonome (Sans API, Sans DB)

Vous ne voulez pas faire tourner de serveur ? Vous pouvez utiliser NoRag directement dans **ChatGPT**, **Claude**, **Gemini**, **Grok**, ou un IDE comme **Antigravity**.

1. Ouvrez le dossier `norag/plugins/`.
2. Ouvrez le fichier correspondant à votre IA (ex: `gpt_instructions.md`).
3. Copiez le **System Prompt** et collez-le dans les instructions personnalisées de l'IA.
4. Dans votre premier message à l'IA, envoyez le contenu des 3 fichiers situés dans `data/` (`index_agents.md`, `index_documents.md`, `index_history.md`).
5. **C'est tout !** L'IA adoptera le comportement NoRag.

*Note relative à Claude Code (Terminal)* : Copiez `norag/plugins/claude_skill.md` dans vos skills Claude pour activer la lecture directe des PDFs locaux sans aucune API.

---

### Mode B : CLI Interactif Local (Avec historique SQLite)

Mode terminal interactif rapide. Il utilise la base de données SQLite locale (`norag.db`) pour sauvegarder les sessions.

```bash
python -m api.local_query
```

> **Exemple de session :**
> Vous > Que dit Charles Gave sur l'inflation ?
> NoRag > Selon [Les Mondes de demain, Pages 41-84], l'inflation...

Commandes disponibles : `/list`, `/archive`, `/quit`.

---

### Mode C : API REST Complète (Backend SQLite Local)

Lance un serveur web qui gère les requêtes, l'historique et l'indexation. Aucune configuration complexe : une base SQLite (`local/norag.db`) est créée automatiquement.

**Configuration `.env` recommandée :**
```env
NORAG_BACKEND=sqlite
SQLITE_DB_PATH=local/norag.db
GEMINI_API_KEY=AIza...
```

**Démarrage :**
```bash
uvicorn api.main:app --reload
```

- L'API tourne sur : `http://localhost:8000`
- Swagger / Documentation interactive : `http://localhost:8000/docs`

Vous y trouverez les endpoints `/index/`, `/query/`, `/documents/`, `/archive/`.

---

### Mode D : API REST Cloud (Backend Supabase PostgreSQL)

Idéal pour déployer NoRag en production sur un VPS ou Vercel. L'historique, les documents et le cache des index sont stockés dans le Cloud sur Supabase.

#### 1. Configuration Supabase
1. Créez un projet sur [supabase.com](https://supabase.com).
2. Allez dans le **SQL Editor**, créez une nouvelle requête et exécutez le script suivant pour générer les tables :

```sql
-- Table des documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY, titre TEXT NOT NULL,
    resume_global TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);

-- Table des chunks (Sections)
CREATE TABLE IF NOT EXISTS chunks_documents (
    id SERIAL PRIMARY KEY, document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    titre_section TEXT NOT NULL, mots_cles TEXT NOT NULL,
    contenu_complet TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);

-- Table de l'historique (Sessions)
CREATE TABLE IF NOT EXISTS memoire_norag (
    id SERIAL PRIMARY KEY, session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    contenu TEXT NOT NULL, cree_le TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON memoire_norag (session_id, cree_le DESC);
```

#### 2. Configuration `.env`
Récupérez vos identifiants dans Supabase (Project Settings -> API) :

```env
NORAG_BACKEND=supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1...
GEMINI_API_KEY=AIza...
```

#### 3. Démarrage
```bash
uvicorn api.main:app --reload
```
L'API pointera automatiquement vers votre base de données en ligne.

---

## 📚 Workflow : Comment ajouter un nouveau document ?

L'objectif est d'alimenter `data/index_documents.md` et Optionnellement la base de données.

Si vous utilisez le mode **Base de données (Mode C ou D)** :
1. Lancez l'API (`uvicorn api.main:app`).
2. Copiez le texte brut de votre chapitre/document PDF.
3. Utilisez le endpoint `POST /archive` (via Swagger ou curl) en envoyant ce texte. L'IA "Archiviste" va structurer le document avec des résumés et des mots-clés.
4. Injectez la réponse de l'archiviste dans la base avec le endpoint `POST /documents`.
5. Utilisez `POST /index/rebuild` pour régénérer le fichier `index_documents.md` sur le disque dur.

Si vous utilisez le mode **Agent Autonome (Mode A)** :
1. Demandez simplement à l'IA : `/archive [collez le contenu de votre PDF ici]`.
2. L'IA va vous répondre avec une fiche structurée.
3. Copiez-collez cette fiche directement dans le fichier `data/index_documents.md`.

---

## 🧱 Structure du projet v2

```text
NoRag/
├── core/                  # Le moteur principal (Indexer, config, storage, index_builder)
├── data/                  # Vos documents et Index en clair
│   ├── index_agents.md    # -> Liste des compétences
│   ├── index_documents.md # -> Mots-clés pour le Routage
│   └── index_history.md   # -> Résumés des conversations
├── api/                   # Interface FastAPI (serveur REST)
├── norag/                 # Utilitaires LLM
│   └── plugins/           # -> Prompts copiable pour Claude, GPT, Gemini, Grok
└── README.md
```
