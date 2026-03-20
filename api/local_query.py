"""
NoRag — Mode local sans base de données.

Utilise directement data/NoRag/index.md comme source de connaissances.
Pipeline en 2 étapes :
  1. ROUTAGE   → Gemini lit l'index + la question → identifie les documents pertinents
  2. GÉNÉRATION → Gemini répond en utilisant uniquement ces documents

Lance avec : python -m api.local_query
Ou          : python NoRag/api/local_query.py
"""

import json
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger .env depuis la racine de NoRag
_NORAG_ROOT = Path(__file__).parent.parent
load_dotenv(_NORAG_ROOT / ".env")

# Chercher index.md dans data/NoRag/ par rapport à la racine du projet
_DATA_INDEX = _NORAG_ROOT.parent / "data" / "NoRag" / "index.md"

# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_ROUTER = """Tu es un routeur documentaire. Tu reçois un index de documents et une question.
Ta seule tâche : identifier les documents pertinents pour répondre à la question.

Réponds UNIQUEMENT avec un objet JSON valide, sans texte autour :
{"documents": ["Titre exact du document 1", "Titre exact du document 2"]}

Règles :
- Les titres doivent correspondre exactement aux titres présents après "## 📄" dans l'index.
- Maximum 3 documents.
- Si aucun document n'est pertinent : {"documents": []}
- Ne génère aucun texte en dehors du JSON."""

SYSTEM_NORAG = """Tu es NoRag, un assistant documentaire expert.
Tu as accès à des extraits sélectionnés d'un index documentaire (fournis dans le contexte).

RÈGLES ABSOLUES :
1. Réponds EXCLUSIVEMENT à partir des informations fournies dans [DOCUMENTS PERTINENTS].
2. Cite ta source à la fin de chaque argument : [Titre du document, Pages X-Y]
3. Si les documents ne contiennent pas la réponse, dis clairement : "Les documents sélectionnés ne me permettent pas de répondre à cette question."
4. Ne devine jamais. Ne génère pas de contenu non sourcé.
5. Maintiens un ton analytique et factuel.

COMMANDES DISPONIBLES :
- /list  → lister tous les documents disponibles
- /quit  → quitter"""


# ── Index parsing ─────────────────────────────────────────────────────────────

def load_index(path: Path) -> str:
    if not path.exists():
        print(f"⚠️  Index non trouvé : {path}")
        print("Vérifiez que data/NoRag/index.md existe.")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def list_doc_titles(index_content: str) -> list[str]:
    """Retourne la liste des titres de documents (après ## 📄)."""
    return [
        line.replace("## 📄", "").strip()
        for line in index_content.splitlines()
        if line.startswith("## 📄")
    ]


def extract_documents(titles: list[str], index_content: str) -> str:
    """Extrait les blocs de l'index correspondant aux titres demandés."""
    if not titles:
        return index_content  # fallback : retourner tout l'index

    # Découper l'index en blocs par document (séparateur : ## 📄)
    blocks = re.split(r'\n(?=## 📄)', index_content.strip())
    selected = []
    for block in blocks:
        for title in titles:
            if title.lower() in block.lower():
                selected.append(block.strip())
                break

    return "\n\n".join(selected) if selected else index_content


# ── Pipeline NoRag local ──────────────────────────────────────────────────────

def route_documents(question: str, index_content: str) -> list[str]:
    """Étape 1 : Gemini identifie les documents pertinents depuis l'index."""
    from api.gemini import appeler_gemini

    prompt = f"[INDEX]\n{index_content}\n\n[QUESTION]\n{question}"
    raw = appeler_gemini(prompt, SYSTEM_ROUTER)

    try:
        m = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if m:
            data = json.loads(m.group())
            return data.get("documents", [])
    except Exception:
        pass
    return []


def generate_answer(question: str, context: str, history: list[dict]) -> str:
    """Étape 2 : Gemini répond en utilisant uniquement les documents sélectionnés."""
    from api.gemini import appeler_gemini

    history_str = "\n".join(f"- {m['role']}: {m['content']}" for m in history[-4:])

    prompt = f"""[HISTORIQUE DE CONVERSATION]
{history_str if history_str else "(aucun)"}

[DOCUMENTS PERTINENTS]
{context}

[QUESTION]
{question}"""

    return appeler_gemini(prompt, SYSTEM_NORAG)


def ask(question: str, index_content: str, history: list[dict]) -> str:
    """Pipeline complet : routage → extraction → génération."""
    # Étape 1 : identifier les documents pertinents
    relevant_titles = route_documents(question, index_content)

    if relevant_titles:
        print(f"  📂 Documents sélectionnés : {', '.join(relevant_titles)}")
    else:
        print("  📂 Aucun document ciblé — utilisation de l'index complet")

    # Étape 2 : extraire uniquement ces documents
    context = extract_documents(relevant_titles, index_content)

    # Étape 3 : générer la réponse
    return generate_answer(question, context, history)


def cmd_list(index_content: str) -> str:
    """Extrait la liste des documents depuis l'index."""
    docs = list_doc_titles(index_content)
    if not docs:
        return "Aucun document trouvé dans l'index."
    return "\n".join(f"  {i+1}. {d}" for i, d in enumerate(docs))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  NoRag — Mode local (sans base de données)")
    print(f"  Index : {_DATA_INDEX}")
    print("=" * 60)
    print("  Tapez votre question, /list ou /quit")
    print()

    index_content = load_index(_DATA_INDEX)
    docs = list_doc_titles(index_content)
    print(f"✅ {len(docs)} document(s) chargé(s) depuis l'index.\n")

    history: list[dict] = []

    while True:
        try:
            question = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir.")
            break

        if not question:
            continue

        if question.lower() in ("/quit", "/exit", "exit", "quit"):
            print("Au revoir.")
            break

        if question.lower() == "/list":
            print("\nDocuments disponibles :")
            print(cmd_list(index_content))
            print()
            continue

        print("\nNoRag > ", end="", flush=True)
        try:
            answer = ask(question, index_content, history)
            print(answer)
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})
        except Exception as e:
            print(f"Erreur : {e}")
        print()


if __name__ == "__main__":
    main()
