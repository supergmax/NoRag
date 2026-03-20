NoRag → Oraculus v2 : Système 3-Index Multi-LLM
Phase 1 — Architecture & Planification
Analyser le codebase existant NoRag
Rédiger le plan d'implémentation (3-index + multi-LLM)
Validation utilisateur du plan
Phase 2 — Moteur d'Indexation (core/)
Créer core/indexer.py : scanner de fichiers, lecture PDF/MD/TXT, extraction de métadonnées
Créer core/index_builder.py : génère les 3 fichiers index en Markdown
Créer core/storage.py : abstraction filesystem / SQLite / Supabase
Créer core/config.py : configuration centralisée (chemins, backend, etc.)
Phase 3 — Les 3 Index
index_agents.md : index des agents/skills/system prompts avec compétences
index_documents.md : index documentaire détaillé (migration de l'existant)
index_history.md : index historique des conversations + résumés
Phase 4 — System Prompt Universel v2
Nouveau system prompt intégrant les 3 index
Adapter le prompt pour Claude / Gemini / Grok / GPT / etc.
Générer les fichiers de skill/plugin par plateforme
Phase 5 — API & CLI Modernisés
Adapter l'API FastAPI aux nouveaux index
Adapter le CLI local aux 3 index
Endpoint /index/rebuild pour régénérer les index
Phase 6 — Vérification
Tests unitaires pour le moteur d'indexation
Test de bout en bout : indexation → query → réponse citée
Test multi-plateforme des prompts générés
