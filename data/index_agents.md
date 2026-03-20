# 🤖 Index des Agents & Skills

*Dernière mise à jour : 2026-03-20 11:18*

## 📋 Vue d'ensemble

| Agent | Domaine | Compétences | Activation |
|-------|---------|-------------|------------|
| NoRag | Q&R documentaire | Routage LLM, citation, archivage | Par défaut |
| Archiviste | Indexation | Extraction PDF, fiches Markdown | /archive |

---

## 🔧 Agent : NoRag
- **Description** : Assistant documentaire expert par routage LLM. Exploite les grandes fenêtres de contexte pour router les questions vers les documents pertinents, sans embeddings vectoriels.
- **System Prompt** : `norag/system_prompt_universel.md`
- **Compétences** :
  - Routage en 2 étapes sur l'index documentaire
  - Réponse citée avec sources [Document, Pages X-Y]
  - Mémoire de conversation par session
  - Navigation multi-documents
- **Commandes** : /list, /sections, /archive, /add
- **Modèles supportés** : Gemini, Claude, GPT-4, Grok, Mistral

---

## 🔧 Agent : Archiviste
- **Description** : Système d'indexation automatique. Analyse un document brut et génère une fiche structurée prête à être ajoutée à l'index documentaire.
- **System Prompt** : `NoRag_Archiviste.md`
- **Compétences** :
  - Analyse de documents bruts (PDF, texte copié-collé)
  - Génération de fiches index structurées en Markdown
  - Découpage intelligent en sections avec mots-clés
  - Résumé global factuel (2-3 phrases)
- **Commandes** : /archive [texte]
- **Modèles supportés** : Gemini, Claude, GPT-4, Grok, Mistral

---
