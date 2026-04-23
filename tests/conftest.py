import os
from pathlib import Path
import pytest

@pytest.fixture
def tmp_project(tmp_path, monkeypatch):
    """Isolated project root for tests."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "documents").mkdir()
    (tmp_path / "core" / "prompts").mkdir(parents=True)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    return tmp_path
