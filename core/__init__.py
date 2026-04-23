"""
NoRag Core — Configuration, indexation, stockage.

Ce module centralise :
- config : configuration (chemins, modèles, constantes)
- indexer : scan et extraction de fichiers (PDF, MD, TXT)
- storage : abstraction de stockage (filesystem / SQLite / Supabase)
"""

from .config import Config, get_config
from .indexer import Indexer
from .storage import get_storage

__all__ = ["Config", "get_config", "Indexer", "get_storage"]
