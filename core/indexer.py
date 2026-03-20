"""
NoRag Core — Indexer.

Scan récursif de fichiers, extraction de texte depuis PDF/MD/TXT,
et extraction de métadonnées pour alimenter l'index documentaire.
"""

import hashlib
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class DocumentMeta:
    """Métadonnées d'un document scanné."""
    title: str
    filepath: Path
    file_type: str  # "pdf", "md", "txt"
    size_bytes: int
    page_count: int = 0
    hash_sha256: str = ""
    scanned_at: str = ""
    sections: list[dict] = field(default_factory=list)


class Indexer:
    """Scanner et extracteur de documents."""

    SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def scan(self, subdirectory: str | None = None) -> list[DocumentMeta]:
        """Scanne le répertoire de données et retourne les métadonnées de chaque fichier."""
        scan_dir = self.data_dir / subdirectory if subdirectory else self.data_dir
        if not scan_dir.exists():
            return []

        results = []
        for filepath in sorted(scan_dir.rglob("*")):
            if filepath.is_file() and filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                meta = self._extract_meta(filepath)
                if meta:
                    results.append(meta)

        return results

    def _extract_meta(self, filepath: Path) -> DocumentMeta | None:
        """Extrait les métadonnées d'un fichier."""
        try:
            stat = filepath.stat()
            file_hash = self._hash_file(filepath)
            ext = filepath.suffix.lower()

            meta = DocumentMeta(
                title=filepath.stem.replace("_", " "),
                filepath=filepath.relative_to(self.data_dir),
                file_type=ext.lstrip("."),
                size_bytes=stat.st_size,
                hash_sha256=file_hash,
                scanned_at=datetime.now().isoformat(),
            )

            if ext == ".pdf":
                meta.page_count = self._count_pdf_pages(filepath)
            elif ext in (".md", ".txt"):
                meta.page_count = self._count_text_lines(filepath)

            return meta
        except Exception:
            return None

    def extract_text(self, filepath: Path) -> str:
        """Extrait le texte intégral d'un fichier."""
        full_path = self.data_dir / filepath if not filepath.is_absolute() else filepath
        ext = full_path.suffix.lower()

        if ext == ".pdf":
            return self._read_pdf(full_path)
        elif ext in (".md", ".txt"):
            return full_path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Type de fichier non supporté : {ext}")

    def extract_pdf_pages(self, filepath: Path, start: int, end: int) -> str:
        """Extrait les pages spécifiques d'un PDF."""
        full_path = self.data_dir / filepath if not filepath.is_absolute() else filepath
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(full_path))
            pages = []
            for i in range(max(0, start - 1), min(end, len(reader.pages))):
                text = reader.pages[i].extract_text()
                if text:
                    pages.append(f"--- Page {i + 1} ---\n{text}")
            return "\n\n".join(pages)
        except ImportError:
            raise RuntimeError("pypdf requis : pip install pypdf")

    @staticmethod
    def _read_pdf(filepath: Path) -> str:
        """Lit tout le texte d'un PDF."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(filepath))
            text_parts = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {i + 1} ---\n{text}")
            return "\n\n".join(text_parts)
        except ImportError:
            raise RuntimeError("pypdf requis : pip install pypdf")

    @staticmethod
    def _count_pdf_pages(filepath: Path) -> int:
        """Compte les pages d'un PDF."""
        try:
            from pypdf import PdfReader
            return len(PdfReader(str(filepath)).pages)
        except Exception:
            return 0

    @staticmethod
    def _count_text_lines(filepath: Path) -> int:
        """Compte les lignes d'un fichier texte."""
        try:
            return sum(1 for _ in filepath.open(encoding="utf-8"))
        except Exception:
            return 0

    @staticmethod
    def _hash_file(filepath: Path) -> str:
        """Calcule le hash SHA-256 d'un fichier."""
        h = hashlib.sha256()
        with filepath.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]  # hash court pour lisibilité
