"""
NoRag Core — Moteur d'indexation et de gestion des 3 index.

Ce module centralise :
- config : configuration (chemins, backend, constantes)
- indexer : scan et extraction de fichiers (PDF, MD, TXT)
- index_builder : génération des 3 fichiers index Markdown
- storage : abstraction de stockage (filesystem / SQLite / Supabase)
"""

from .config import Config
from .indexer import Indexer
from .index_builder import IndexBuilder
from .storage import get_storage

__all__ = ["Config", "Indexer", "IndexBuilder", "get_storage"]
