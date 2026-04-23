---
name: norag
description: Query documents in the NoRag knowledge base using L1 (2-call pipeline) or Multi_L (parallel perspectives + synthesis). Trigger on /norag or when user asks to search documents with NoRag.
---

# NoRag Skill — L1 & Multi_L

Ce skill implémente les deux pipelines NoRag directement dans Claude Code, en lisant les fichiers locaux sans API externe.

## Variables de contexte

Avant tout, identifie le répertoire racine NoRag (là où se trouvent `data/index.md` et `data/index_system_prompt.md`). Par défaut : le répertoire de travail courant.

```
INDEX_PATH      = <root>/data/index.md
AGENTS_PATH     = <root>/data/index_system_prompt.md
DOCUMENTS_DIR   = <root>/data/documents/
```

---

## Pipeline NoRag L1 (défaut)

**Utilise L1 quand** : question directe, un angle suffisant, vitesse souhaitée.

### Étape 1 — ROUTAGE (silencieux, ne pas afficher)

Lis `data/index.md` ET `data/index_system_prompt.md`.

En te basant sur la question, détermine :
- **`agent_id`** : l'agent le mieux adapté dans `index_system_prompt.md` (cherche `## <agent_id>` et lis sa description + "Quand l'utiliser")
- **`documents`** : 1 à 3 entrées de `index.md` avec leurs `section_id` pertinentes

Ne montre pas le résultat du routage à l'utilisateur.

### Étape 2 — LECTURE DES SECTIONS

Pour chaque `(doc_id, [section_id, ...])` sélectionné, lis le fichier :
```
Read: data/documents/<doc_id>.md
```
Extrais uniquement les sections `## <section_id>` identifiées.

Si un fichier est absent : note-le silencieusement, continue avec les autres.

### Étape 3 — RÉPONSE

Adopte le system prompt de l'agent sélectionné (bloc "> ..." sous `**System prompt**` dans `index_system_prompt.md`).

Réponds en citant obligatoirement : `[doc_id, section_id]`

Si aucun document ne couvre la question : dis-le explicitement, ne devine pas.

---

## Pipeline NoRag Multi_L

**Utilise Multi_L quand** : question complexe, multi-angles, ou l'utilisateur précise `mode=MultiL` ou un preset.

### Presets disponibles

| Preset | Description |
|---|---|
| **A** | Même question, agents différents (perspectives croisées) |
| **B** | Question décomposée en sous-questions, même agent |
| **C** | Même question, agents différents, sous-ensembles de docs différents |
| **D** | Hybride auto — tu choisis la meilleure combinaison |

### Étape 1 — PLANIFICATION (silencieuse)

Lis `data/index.md` et `data/index_system_prompt.md`.

Construis un plan de layers. Chaque layer = `(agent_id, question_du_layer, doc_scope)`.

Exemple pour preset A sur "Faut-il adopter le cloud AWS ?" :
```
Layer 1: agent=analyste_technique,  question="Faut-il adopter AWS ?", scope=all
Layer 2: agent=juriste_conformite,  question="Faut-il adopter AWS ?", scope=all
Layer 3: agent=analyste_finance,    question="Faut-il adopter AWS ?", scope=all
```

### Étape 2 — EXÉCUTION DES LAYERS

Pour chaque layer, exécute L1 complet (routage + lecture + réponse partielle).

Affiche brièvement le layer en cours : `> Layer N (agent: <id>)...`

### Étape 3 — AGRÉGATION

Synthétise toutes les réponses en :
1. Structurant par perspective (preset A), sous-question (B), ou corpus (C)
2. Nommant explicitement les contradictions entre layers
3. Conservant toutes les citations `[doc_id, section_id]`
4. Concluant par un paragraphe **Synthèse**

---

## Commandes

| Commande | Action |
|---|---|
| `/norag <question>` | L1 sur la question |
| `/norag multi_l <question>` | Multi_L preset D (auto) |
| `/norag multi_l A <question>` | Multi_L preset A (multi-agent) |
| `/norag multi_l B <question>` | Multi_L preset B (décomposition) |
| `/norag multi_l C <question>` | Multi_L preset C (multi-corpus) |
| `/norag list` | Lister tous les docs dans `data/index.md` |
| `/norag agents` | Lister tous les agents dans `index_system_prompt.md` |
| `/norag ingest <doc_id>` | Générer une fiche index pour un texte collé ensuite |

---

## Commande `/norag ingest <doc_id>`

L'utilisateur colle le texte brut du document. Tu génères :

**1. Une fiche pour `data/index.md`** au format exact :
```markdown
## <doc_id>
- **Titre** : ...
- **Résumé** : ...
- **Sections** :
  - `<section_id>` — <titre section> — mots-clés : ...
```

**2. Le fichier `data/documents/<doc_id>.md`** structuré en sections :
```markdown
## <section_id_1>
<contenu complet de la section>

## <section_id_2>
<contenu complet>
```

Écris les deux fichiers directement avec le Write tool, puis dis à l'utilisateur d'ajouter la fiche dans `data/index.md`.

---

## Règles absolues

1. **Citations obligatoires** : chaque affirmation factuellement issue d'un document doit citer `[doc_id, section_id]`
2. **Pas d'invention** : si l'info n'est pas dans les documents, dis-le
3. **Routage silencieux** : l'étape de routage ne s'affiche pas
4. **Sections complètes** : lis la section entière, pas un extrait
5. **Multi_L** : montre les layers progressivement, puis la synthèse finale
