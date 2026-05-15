from __future__ import annotations

from dataclasses import dataclass

DEFAULT_ENDPOINT = "https://brianchenhao-chenki-llm.hf.space/v1"
DEFAULT_MODEL = "qwen2.5-1.5b-instruct"
DEFAULT_TIMEOUT = 60.0
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_RETRIES = 1
DEFAULT_RETRY_BACKOFF_BASE = 0.5
DEFAULT_CACHE_PATH = "chenki_cache.db"


@dataclass
class ChenkiConfig:
    endpoint: str = DEFAULT_ENDPOINT
    model: str = DEFAULT_MODEL
    timeout: float = DEFAULT_TIMEOUT
    temperature: float = DEFAULT_TEMPERATURE
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff_base: float = DEFAULT_RETRY_BACKOFF_BASE
    cache_enabled: bool = False
    cache_path: str = DEFAULT_CACHE_PATH
