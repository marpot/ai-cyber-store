"""Lightweight language detection.

Uses ``langdetect`` when available; if not (e.g. during early bootstrap or
in restricted test envs) we fall back to a small ASCII-vs-diacritics
heuristic that still distinguishes Polish from English well enough for
the recommendation UI.

Public API:

    detect_language(text: str) -> str  # returns "pl" | "en" | "unknown"
"""
from __future__ import annotations

import re
from functools import lru_cache

try:
    from langdetect import DetectorFactory, detect_langs  # type: ignore

    DetectorFactory.seed = 42  # deterministic results across runs.
    _LANGDETECT_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    detect_langs = None
    _LANGDETECT_AVAILABLE = False

# Polish-specific diacritics (a-z extended). Their presence is a strong
# signal that the text is Polish, not English.
_POLISH_DIACRITICS = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")
# Common Polish function words.
_POLISH_HINT_WORDS = {
    "jak",
    "co",
    "się",
    "mam",
    "mój",
    "moja",
    "moje",
    "potrzebuję",
    "chcę",
    "czy",
    "jest",
    "nie",
    "tak",
}
_ENGLISH_HINT_WORDS = {
    "the",
    "how",
    "what",
    "i",
    "you",
    "my",
    "is",
    "are",
    "do",
    "need",
    "want",
    "protect",
}


def _heuristic_language(text: str) -> str:
    lowered = text.lower()
    words = set(re.findall(r"\b\w+\b", lowered))
    pl_score = len(words & _POLISH_HINT_WORDS) + (3 if _POLISH_DIACRITICS.search(text) else 0)
    en_score = len(words & _ENGLISH_HINT_WORDS)
    if pl_score > en_score and pl_score > 0:
        return "pl"
    if en_score > pl_score:
        return "en"
    if pl_score == en_score and pl_score > 0:
        # Tie-break in favour of Polish diacritics.
        return "pl" if _POLISH_DIACRITICS.search(text) else "en"
    return "unknown"


@lru_cache(maxsize=2048)
def detect_language(text: str) -> str:
    """Return ISO 639-1 code for the most probable language of ``text``.

    Cached because detection is somewhat expensive and the same user
    inputs tend to repeat (chats, smoke tests).
    """
    if not text or not text.strip():
        return "unknown"

    if _LANGDETECT_AVAILABLE:
        assert detect_langs is not None
        try:
            results = detect_langs(text)
            if results:
                top = results[0]
                # langdetect returns "pl", "en", etc. with a probability.
                if top.prob >= 0.7:
                    code = top.lang
                    if code in {"pl", "en"}:
                        return code
                    # Map common variants.
                    if code.startswith("pl"):
                        return "pl"
                    if code.startswith("en"):
                        return "en"
        except Exception:
            # Detector can raise on very short or noisy input.
            pass

    return _heuristic_language(text)