"""Optional LLM fallback for low-confidence queries.

Disabled by default — only activates when ``LLM_API_KEY`` is set in the
environment. Uses any OpenAI-compatible chat completions endpoint
(OpenRouter free models, local Ollama, llama.cpp server, etc.).

The LLM is invoked only when:

1. The local intent classifier returned ``general_query`` or low
   confidence (< ``RECOMMENDATION_CONFIDENCE_THRESHOLD``).
2. The fuzzy product search produced nothing useful.

This keeps the service free and offline by default while letting
operators upgrade it to a hosted LLM by simply setting two env vars.
"""
from __future__ import annotations

import logging
from typing import Iterable

import httpx

from .config import get_settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a concise cybersecurity product advisor for an online store "
    "selling antivirus, VPN, password managers, and similar tools. "
    "Reply in the same language the user used. Keep replies under 60 words. "
    "Do not invent product names — recommend only from the catalogue if asked."
)


def llm_enabled() -> bool:
    return bool(get_settings().llm_api_key)


def chat(
    user_message: str,
    *,
    history: Iterable[dict] = (),
    timeout: float = 6.0,
) -> str | None:
    """Return the LLM's reply, or ``None`` if disabled / failed.

    ``history`` is a sequence of ``{"role": ..., "content": ...}`` dicts
    following the OpenAI chat-completions schema.
    """
    settings = get_settings()
    if not settings.llm_api_key:
        return None

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": 200,
    }

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, httpx.RequestError, ValueError) as exc:
        logger.warning("LLM call failed (%s)", exc)
        return None

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return None