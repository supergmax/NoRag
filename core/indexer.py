"""Archivist ingestion: raw text → (index card in index.md, document file)."""

from dataclasses import dataclass, field

from core.config import Config
from core.llm_client import LLMClient
from core.storage import Storage


ARCHIVIST_SYSTEM = """Tu es l'Archiviste NoRag. À partir d'un texte brut et d'un doc_id, tu produis deux blocs séparés par `---DOCUMENT---`.

**Bloc 1 — fiche index** (au format exact pour data/index.md) :

## <doc_id>
- **Titre** : ...
- **Résumé** : ...
- **Sections** :
  - `<section_id>` — <titre section> — mots-clés : ...

---DOCUMENT---

**Bloc 2 — document structuré** en sections ## <section_id> :

## <section_id_1>
<contenu complet de la section>

## <section_id_2>
<contenu complet>

Règles :
- Reprends le `doc_id` fourni exactement comme id de section racine.
- Sections complètes, jamais de chunking arbitraire.
- Aucun texte hors des deux blocs.
- Le séparateur est exactement : ---DOCUMENT---
"""


@dataclass
class Indexer:
    config: Config
    storage: Storage
    llm: LLMClient = field(default=None)

    def __post_init__(self):
        if self.llm is None:
            self.llm = LLMClient(api_key=self.config.gemini_api_key)

    async def ingest(self, doc_id: str, raw_text: str) -> dict:
        user = f"# doc_id\n{doc_id}\n\n# texte brut\n{raw_text}\n"
        resp = await self.llm.generate(
            model=self.config.answer_model,
            system=ARCHIVIST_SYSTEM,
            user=user,
        )
        if "---DOCUMENT---" not in resp.text:
            raise ValueError(
                f"Archivist response missing ---DOCUMENT--- separator. Got: {resp.text[:200]}"
            )

        card, document = resp.text.split("---DOCUMENT---", 1)
        card = card.strip()
        document = document.strip()

        existing = (
            self.config.index_path.read_text(encoding="utf-8")
            if self.config.index_path.exists()
            else ""
        )
        if existing and not existing.endswith("\n"):
            existing += "\n"
        self.config.index_path.write_text(
            existing + "\n" + card + "\n", encoding="utf-8"
        )

        doc_path = self.config.documents_dir / f"{doc_id}.md"
        doc_path.write_text(document + "\n", encoding="utf-8")

        return {"doc_id": doc_id, "tokens": resp.tokens}
