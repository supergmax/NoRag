from core.config import Config

def test_config_defaults(tmp_project, monkeypatch):
    monkeypatch.delenv("DEFAULT_MODE", raising=False)
    monkeypatch.delenv("ROUTER_MODEL", raising=False)
    monkeypatch.delenv("ANSWER_MODEL", raising=False)
    monkeypatch.delenv("AGGREGATOR_MODEL", raising=False)
    monkeypatch.delenv("MULTIL_MAX_LAYERS", raising=False)
    monkeypatch.delenv("MULTIL_LAYER_TIMEOUT_S", raising=False)
    cfg = Config(project_root=tmp_project)
    assert cfg.default_mode == "L1"
    assert cfg.router_model == "gemini-2.5-flash-lite"
    assert cfg.answer_model == "gemini-2.5-pro"
    assert cfg.aggregator_model == "gemini-2.5-pro"
    assert cfg.multil_max_layers == 3
    assert cfg.multil_layer_timeout_s == 30
    assert cfg.index_path == tmp_project / "data" / "index.md"
    assert cfg.system_prompt_path == tmp_project / "data" / "index_system_prompt.md"
    assert cfg.documents_dir == tmp_project / "data" / "documents"
    assert cfg.prompts_dir == tmp_project / "core" / "prompts"

def test_config_env_overrides(tmp_project, monkeypatch):
    monkeypatch.setenv("DEFAULT_MODE", "MultiL")
    monkeypatch.setenv("ROUTER_MODEL", "custom-slm")
    monkeypatch.setenv("MULTIL_MAX_LAYERS", "5")
    cfg = Config(project_root=tmp_project)
    assert cfg.default_mode == "MultiL"
    assert cfg.router_model == "custom-slm"
    assert cfg.multil_max_layers == 5
