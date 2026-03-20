import os
import re
import json
from pathlib import Path
from google import genai
from google.genai import types

# Charger les system prompts depuis les fichiers existants
_ROOT = Path(__file__).parent.parent

def _read(filename: str) -> str:
    return (_ROOT / filename).read_text(encoding="utf-8")


SYSTEM_ARCHIVISTE = _read("NoRag_Archiviste.md")
SYSTEM_ROUTEUR = """Tu es un routeur. Analyse la question et choisis les IDs des chunks correspondants dans l'index fourni. Renvoie UNIQUEMENT un JSON valide."""
SYSTEM_GENERATEUR = """Tu es NoRag, un assistant analytique factuel. Réponds EXCLUSIVEMENT à partir des documents extraits fournis en contexte. Cite tes sources à la fin de chaque argument (ex: [Document X, Section Y]). Si les documents ne contiennent pas la réponse, dis-le clairement."""


def _client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY manquant dans les variables d'environnement.")
    return genai.Client(api_key=api_key)


def nettoyer_json(texte: str) -> str:
    match = re.search(r"\{.*\}", texte, re.DOTALL)
    return match.group(0) if match else "{}"


def appeler_gemini(prompt: str, system_instruction: str, temperature: float = 0.2) -> str:
    client = _client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )
    return response.text


def router(index_virtuel: str, question: str) -> list[int]:
    """Étape 1 : demande au LLM routeur quels chunk IDs utiliser."""
    prompt = f"""[INDEX]
{index_virtuel}

[QUESTION]
{question}

Renvoie UNIQUEMENT un JSON. Format : {{"chunks_ids": [1, 2]}}. Si rien ne correspond : {{"chunks_ids": []}}."""
    raw = appeler_gemini(prompt, SYSTEM_ROUTEUR)
    try:
        data = json.loads(nettoyer_json(raw))
        return [int(i) for i in data.get("chunks_ids", [])]
    except Exception:
        return []


def generate(memory: str, context: str, question: str) -> str:
    """Étape 2 : génère la réponse finale avec le contexte extrait."""
    prompt = f"""[HISTORIQUE]
{memory}

[DOCUMENTS EXTRAITS]
{context}

[QUESTION]
{question}"""
    return appeler_gemini(prompt, SYSTEM_GENERATEUR)


def archive(texte_brut: str) -> str:
    """Archive un texte brut en fiche Markdown structurée (index.md format)."""
    return appeler_gemini(texte_brut, SYSTEM_ARCHIVISTE, temperature=0.1)
