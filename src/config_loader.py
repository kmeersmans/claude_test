"""Load and validate YAML configuration files."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class Criterion(BaseModel):
    id: str
    name: str
    description: str
    scale_min: int
    scale_max: int
    guidelines: dict[int, str]


class CriteriaConfig(BaseModel):
    criteria: list[Criterion]


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3.1:8b"
    temperature: float = 0.1
    num_ctx: int = 8192


class BedrockConfig(BaseModel):
    region: str = "us-east-1"
    model_id: str = "anthropic.claude-sonnet-4-20250514"
    temperature: float = 0.1
    max_tokens: int = 4096
    profile: str | None = None


class LLMConfig(BaseModel):
    active_provider: str
    ollama: OllamaConfig = OllamaConfig()
    bedrock: BedrockConfig = BedrockConfig()
    system_preamble: str = ""


def _load_yaml(filename: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename
    with open(path) as f:
        return yaml.safe_load(f)


def load_criteria() -> CriteriaConfig:
    data = _load_yaml("criteria.yaml")
    return CriteriaConfig(**data)


def load_llm_config() -> LLMConfig:
    data = _load_yaml("llm_config.yaml")
    return LLMConfig(**data)
