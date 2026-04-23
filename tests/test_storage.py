from core.storage import Storage

def test_read_index(tmp_project):
    (tmp_project / "data" / "index.md").write_text("# index\n- doc1", encoding="utf-8")
    (tmp_project / "data" / "index_system_prompt.md").write_text("# agents\n## default", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    assert "doc1" in s.read_index()
    assert "default" in s.read_system_prompts()

def test_read_document_section(tmp_project):
    docs = tmp_project / "data" / "documents"
    (docs / "acme.md").write_text("## art_7\nContent A\n## art_8\nContent B", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data", documents_dir=docs)
    content = s.read_document_sections("acme", ["art_7"])
    assert "Content A" in content
    assert "Content B" not in content

def test_read_document_all_sections_when_empty_list(tmp_project):
    docs = tmp_project / "data" / "documents"
    (docs / "full.md").write_text("## s1\nA\n## s2\nB", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data", documents_dir=docs)
    content = s.read_document_sections("full", [])
    assert "A" in content
    assert "B" in content

def test_read_document_missing_returns_empty(tmp_project):
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    assert s.read_document_sections("nope", ["x"]) == ""

def test_extract_agent_prompt(tmp_project):
    (tmp_project / "data" / "index_system_prompt.md").write_text(
        "## default\n**Description** : fallback\n**System prompt** :\n> Be helpful.\n\n## other\n**System prompt** :\n> Other prompt.\n",
        encoding="utf-8"
    )
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    prompt = s.extract_agent_prompt("default")
    assert prompt is not None
    assert "Be helpful" in prompt

def test_extract_agent_prompt_missing_returns_none(tmp_project):
    (tmp_project / "data" / "index_system_prompt.md").write_text("## default\n> x\n", encoding="utf-8")
    s = Storage(data_dir=tmp_project / "data",
                documents_dir=tmp_project / "data" / "documents")
    assert s.extract_agent_prompt("nonexistent") is None
