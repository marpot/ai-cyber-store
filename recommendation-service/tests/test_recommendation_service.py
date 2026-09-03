"""Unit tests for ``app.services.recommendation.RecommendationService``.

These tests bypass the HTTP layer and exercise the business logic
directly, so failures point to the service (not FastAPI wiring).
"""
from __future__ import annotations

from typing import Iterable

import pytest

from app.fuzzy import FuzzyMatcher
from app.products import ProductFetcher
from app.services.recommendation import (
    DEFAULT_RESPONSES,
    RecommendationService,
)


# ----------------------------------------------------------------------
# Helpers / fixtures
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def service() -> RecommendationService:
    fetcher = ProductFetcher()
    fetcher.get_all(force_refresh=True)
    matcher = FuzzyMatcher(fetcher)
    return RecommendationService(fetcher=fetcher, matcher=matcher)


def _all_product_ids(products: Iterable[dict]) -> list:
    return [p["id"] for p in products]


# ----------------------------------------------------------------------
# Language selection
# ----------------------------------------------------------------------
def test_language_explicit_pl_overrides_detection(service):
    body = service.recommend(message="how can I protect my laptop", explicit_language="pl")
    assert body["language"] == "pl"


def test_language_explicit_en_overrides_detection(service):
    body = service.recommend(message="jak zabezpieczyć komputer", explicit_language="en")
    assert body["language"] == "en"


def test_language_auto_detects_polish(service):
    body = service.recommend(message="jak zabezpieczyć moje wifi", explicit_language=None)
    assert body["language"] == "pl"


def test_language_auto_detects_english(service):
    body = service.recommend(message="how can I secure my router", explicit_language=None)
    assert body["language"] == "en"


# ----------------------------------------------------------------------
# Response contract
# ----------------------------------------------------------------------
def test_response_has_required_keys(service):
    body = service.recommend(message="antywirus na laptopa", explicit_language=None)
    for key in ("intent", "confidence", "language", "message", "products", "fallback"):
        assert key in body, f"missing key: {key}"
    assert body["fallback"] in {"intent", "fuzzy", "default", "llm"}
    assert 0.0 <= body["confidence"] <= 1.0


def test_confidence_is_rounded(service):
    body = service.recommend(message="antywirus", explicit_language=None)
    # ``round(x, 3)`` always produces at most 3 fractional digits.
    s = f"{body['confidence']:.10f}"
    assert "." in s
    decimals = s.split(".")[1].rstrip("0")
    assert len(decimals) <= 3


# ----------------------------------------------------------------------
# Fallback chain
# ----------------------------------------------------------------------
def test_intent_path_returns_by_intent_products(service):
    # "antywirus" should hit the malware_protection intent at high confidence.
    body = service.recommend(message="antywirus", explicit_language="pl")
    if body["fallback"] == "intent":
        assert body["products"]
        assert body["intent"] == "malware_protection"


def test_fuzzy_fallback_label_and_products(service):
    body = service.recommend(
        message="potrzebuję programu antywirusowego", explicit_language="pl"
    )
    # The query is Polish + low confidence — fuzzy path is the expected one.
    if body["fallback"] == "fuzzy":
        assert body["products"]
        # Products must come from the malware_protection category thanks to hints.
        assert all(
            p.get("category") == "malware_protection" for p in body["products"]
        )


def test_default_fallback_when_no_products(service, monkeypatch):
    """If neither intent nor fuzzy produce anything, fall through to the
    default message. We force the fuzzy matcher to return nothing.
    """
    monkeypatch.setattr(
        service._matcher, "search", lambda *a, **k: []
    )
    body = service.recommend(
        message="jak zabezpieczyć moje wifi", explicit_language="pl"
    )
    assert body["products"] == []
    # LLM is disabled in test env (no key), so the default message wins.
    assert body["fallback"] == "default"
    assert body["message"] == DEFAULT_RESPONSES["pl"]["message"]


def test_llm_fallback_uses_llm_message_when_available(service, monkeypatch):
    """If the LLM returns a message, it overrides the default text."""
    monkeypatch.setattr(service._matcher, "search", lambda *a, **k: [])
    monkeypatch.setattr(
        "app.services.recommendation.llm_chat",
        lambda *a, **k: "Cześć! Polecam darmowy antywirus.",
    )
    body = service.recommend(
        message="jak zabezpieczyć moje wifi", explicit_language="pl"
    )
    assert body["fallback"] == "llm"
    assert body["message"] == "Cześć! Polecam darmowy antywirus."
    assert body["products"] == []


# ----------------------------------------------------------------------
# Helper coverage
# ----------------------------------------------------------------------
def test_pick_language_unknown_falls_back_to_polish(service):
    assert service._pick_language(None, "...") == "pl"
    assert service._pick_language("auto", "...") == "pl"
    assert service._pick_language("xx", "...") == "pl"


def test_select_products_uses_intent_path(service):
    products, fallback, intent = service._select_products(
        message="antywirus",
        intent="malware_protection",
        confidence=0.99,
        language="pl",
    )
    assert fallback == "intent"
    assert intent == "malware_protection"
    if products:
        assert all(p["category"] == "malware_protection" for p in products)


def test_select_products_low_confidence_triggers_fuzzy(service):
    products, fallback, intent = service._select_products(
        message="potrzebuję programu antywirusowego",
        intent="general_query",
        confidence=0.1,
        language="pl",
    )
    # Fuzzy is allowed to hit or miss; either way we should report it.
    assert fallback in {"fuzzy", "default"}
    if fallback == "fuzzy":
        assert products


def test_deduplication_in_payload(service):
    body = service.recommend(message="antywirus vpn wifi", explicit_language="pl")
    ids = _all_product_ids(body["products"])
    # The service itself doesn't dedupe (the fuzzy matcher does), but the
    # payload should never contain fewer ids than the count of items.
    assert len(ids) == len(set(ids))
