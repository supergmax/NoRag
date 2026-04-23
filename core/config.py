"""NoRag configuration. Loads .env and exposes typed settings."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class Config:
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    # Paths
    data_dir: Path = field(default=None)
    documents_dir: Path = field(default=None)
    prompts_dir: Path = field(default=None)
    index_path: Path = field(default=None)
    system_prompt_path: Path = field(default=None)

    # LLM
    gemini_api_key: str = ""
    router_model: str = "gemini-2.5-flash-lite"
    answer_model: str = "gemini-2.5-pro"
    aggregator_model: str = "gemini-2.5-pro"

    # Pipeline
    default_mode: str = "L1"
    multil_max_layers: int = 3
    multil_layer_timeout_s: int = 30

    def __post_init__(self):
        load_dotenv(self.project_root / ".env")

        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.documents_dir is None:
            self.documents_dir = self.data_dir / "documents"
        if self.prompts_dir is None:
            self.prompts_dir = self.project_root / "core" / "prompts"
        if self.index_path is None:
            self.index_path = self.data_dir / "index.md"
        if self.system_prompt_path is None:
            self.system_prompt_path = self.data_dir / "index_system_prompt.md"

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", self.gemini_api_key)
        self.router_model = os.getenv("ROUTER_MODEL", self.router_model)
        self.answer_model = os.getenv("ANSWER_MODEL", self.answer_model)
        self.aggregator_model = os.getenv("AGGREGATOR_MODEL", self.aggregator_model)

        self.default_mode = os.getenv("DEFAULT_MODE", self.default_mode)
        self.multil_max_layers = int(os.getenv("MULTIL_MAX_LAYERS", self.multil_max_layers))
        self.multil_layer_timeout_s = int(os.getenv("MULTIL_LAYER_TIMEOUT_S", self.multil_layer_timeout_s))

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)


_config: Config | None = None


def get_config(**kwargs) -> Config:
    global _config
    if _config is None or kwargs:
        _config = Config(**kwargs)
    return _config
