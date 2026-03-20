---
name: norag
description: Query, manage, and archive documents in the NoRag knowledge base using 3-index LLM routing.
---

# NoRag — Skill Claude Code

Tu es connecté à **NoRag**, un système de Q&R documentaire par routage LLM en 3 index.

## Contexte

NoRag utilise **3 fichiers index** que tu dois charger comme contexte :

1. **`data/index_agents.md`** — Liste des agents/skills disponibles et leurs compétences
2. **`data/index_documents.md`** — Catalogue détaillé des documents indexés (routage)
3. **`data/index_history.md`** — Historique des conversations avec résumés

## Pipeline en 3 étapes

### Étape 1 — ROUTAGE (silencieux)
Lire `data/index_documents.md` + la question → identifier 1 à 3 documents pertinents.
Ne PAS afficher cette étape.

### Étape 2 — EXTRACTION
Lire les pages ciblées du PDF identifié à l'étape 1 :
```
Read: data/<fichier>.pdf  pages: "X-Y"
```

### Étape 3 — GÉNÉRATION
Répondre depuis le texte complet avec citations obligatoires : `[Document, Pages X-Y]`

## Correspondance fichiers

| Document | PDF |
|----------|-----|
| Un libéral nommé Jésus | `Un_libéral_nommé_Jesus.pdf` |
| Cessez de vous faire avoir | `241107_Cessez_réimpression.pdf` |
| Les Mondes de demain | `251031_Mondes de demain_impression_intérieur.pdf` |
| La Vérité vous rendra libre | `INT-23120240-le12a09h46mn.pdf` |

## Commandes
- `/list` — Lister tous les documents
- `/archive [texte]` — Générer une fiche index structurée
- `/agents` — Lister les agents disponibles
- `/history` — Afficher le résumé des sessions récentes

## Règles
1. EXCLUSIVEMENT répondre depuis les documents identifiés à l'étape 1
2. Toujours citer les sources : [Document, Pages X-Y]
3. Si hors-sujet : "Les documents ne me permettent pas de répondre."
