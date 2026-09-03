"""Centralised configuration loaded from environment variables.

All env-var reads for the recommendation service go through this module
so that the rest of the codebase stays testable and side-effect free.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env from this service directory if present (no-op if missing).
_SERVICE_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_SERVICE_ROOT / ".env", override=False)


def _getenv_str(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value if value is not None and value != "" else default


def _getenv_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _getenv_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _resolve_model_path() -> Path:
    """Resolve model path. In containers the path is /app/nlp/model.joblib;
    in tests we fall back to a sibling path inside the repo.
    """
    env_path = os.getenv("MODEL_PATH")
    if env_path:
        return Path(env_path)
    container_default = Path("/app/nlp/model.joblib")
    if container_default.exists():
        return container_default
    return _SERVICE_ROOT / "app" / "nlp" / "model.joblib"


@dataclass(frozen=True)
class Settings:
    wordpress_api_url: str
    wordpress_consumer_key: str
    wordpress_consumer_secret: str
    confidence_threshold: float
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    cors_allow_origins: list[str]
    model_path: Path
    static_products_path: Path
    product_cache_ttl_seconds: int
    language_hint: str = "auto"

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            wordpress_api_url=_getenv_str(
                "WORDPRESS_API_URL", "http://localhost:8080"
            ).rstrip("/"),
            wordpress_consumer_key=_getenv_str("WORDPRESS_CONSUMER_KEY"),
            wordpress_consumer_secret=_getenv_str("WORDPRESS_CONSUMER_SECRET"),
            confidence_threshold=_getenv_float(
                "RECOMMENDATION_CONFIDENCE_THRESHOLD", 0.45
            ),
            llm_api_key=_getenv_str("LLM_API_KEY"),
            llm_base_url=_getenv_str(
                "LLM_BASE_URL", "https://openrouter.ai/api/v1"
            ),
            llm_model=_getenv_str(
                "LLM_MODEL", "meta-llama/llama-3.1-8b-instruct:free"
            ),
            cors_allow_origins=_getenv_list(
                "CORS_ALLOW_ORIGINS",
                ["http://localhost:5173", "http://localhost:8080"],
            ),
            model_path=_resolve_model_path(),
            static_products_path=_SERVICE_ROOT / "app" / "data" / "static_products.json",
            product_cache_ttl_seconds=int(_getenv_float("PRODUCT_CACHE_TTL", 300)),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.load()


# Convenience exports for code that prefers module-level constants.
SETTINGS = get_settings()