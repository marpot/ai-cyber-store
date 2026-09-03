"""Recommendation business logic.

This module owns the recommendation pipeline. The HTTP layer
(``app.main``) is intentionally kept thin — it only parses the request,
delegates here, and returns the result.

Fallback chain (preserved from the original implementation):

    intent classifier
            ↓
    confidence check
            ↓
    fuzzy matching
            ↓
    products catalogue
            ↓
    LLM / default fallback
"""
from __future__ import annotations

from typing import Optional

from ..config import SETTINGS
from ..fuzzy import FuzzyMatcher
from ..language import detect_language
from ..llm import chat as llm_chat
from ..nlp.predict import DEFAULT_INTENT, predict_intent
from ..products import ProductFetcher


# ----------------------------------------------------------------------
# Default fallback messages (localised).
# ----------------------------------------------------------------------
DEFAULT_RESPONSES: dict[str, dict[str, str]] = {
    "pl": {
        "message": (
            "Chętnie pomogę w kwestiach cyberbezpieczeństwa! "
            "Zapytaj mnie o ochronę urządzeń, sieci, haseł, prywatności "
            "lub usuwanie wirusów."
        ),
        "intent": DEFAULT_INTENT,
    },
    "en": {
        "message": (
            "Happy to help with cybersecurity questions! "
            "Ask me about device, network, password, or privacy protection, "
            "or malware removal."
        ),
        "intent": DEFAULT_INTENT,
    },
}


# Short, localised user-facing replies for the successful recommendation paths.
_MESSAGE_TEMPLATES: dict[str, dict[str, str]] = {
    "pl": {
        "intent": "Na podstawie Twojego pytania polecam następujące produkty:",
        "fuzzy": "Nie byłem pewny kategorii, ale znalazłem pasujące produkty:",
        "default": DEFAULT_RESPONSES["pl"]["message"],
    },
    "en": {
        "intent": "Based on your question, I recommend these products:",
        "fuzzy": "I wasn't sure about the category, but here are matching products:",
        "default": DEFAULT_RESPONSES["en"]["message"],
    },
}


class RecommendationService:
    """Encapsulates the recommendation pipeline.

    Collaborators are injected so the service is testable and the HTTP
    layer does not need to know how products, fuzzy, or NLP are wired.
    """

    def __init__(
        self,
        *,
        fetcher: ProductFetcher,
        matcher: FuzzyMatcher,
    ) -> None:
        self._fetcher = fetcher
        self._matcher = matcher

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def recommend(
        self,
        *,
        message: str,
        explicit_language: Optional[str] = None,
    ) -> dict:
        """Run the full recommendation pipeline for one user message."""

        language = self._pick_language(explicit_language, message)
        intent, confidence, _classes = predict_intent(message)

        products, fallback, intent = self._select_products(
            message=message,
            intent=intent,
            confidence=confidence,
            language=language,
        )

        if not products:
            # Last resort — surface the default help message, optionally
            # enriched by the LLM.
            default = DEFAULT_RESPONSES.get(language, DEFAULT_RESPONSES["pl"])
            llm_message = llm_chat(message)
            return {
                "intent": intent,
                "confidence": round(confidence, 3),
                "language": language,
                "message": llm_message or default["message"],
                "products": [],
                "fallback": "llm" if llm_message else "default",
            }

        return {
            "intent": intent,
            "confidence": round(confidence, 3),
            "language": language,
            "message": self._build_message(intent, language, fallback),
            "products": products,
            "fallback": fallback,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_language(explicit: Optional[str], fallback_text: str) -> str:
        """Decide which language to render the response in.

        Order:
            1. Explicit override (``pl``/``en``).
            2. Auto-detection from the message text.
            3. ``pl`` as a safe default.
        """
        if explicit and explicit.lower() in {"pl", "en"}:
            return explicit.lower()
        detected = detect_language(fallback_text)
        if detected in {"pl", "en"}:
            return detected
        return "pl"

    @staticmethod
    def _build_products_payload(
        products: list[dict],
        language: str,
    ) -> list[dict]:
        """Project raw products into API-friendly dictionaries."""
        out: list[dict] = []
        for product in products:
            if language == "en":
                display_name = product.get("name") or product.get("name_pl")
                display_description = (
                    product.get("description") or product.get("description_pl")
                )
                display_price = product.get("price") or product.get("price_pl")
            else:
                display_name = product.get("name_pl") or product.get("name")
                display_description = (
                    product.get("description_pl") or product.get("description")
                )
                display_price = product.get("price_pl") or product.get("price")
            out.append(
                {
                    "id": product.get("id"),
                    "name": display_name,
                    "category": product.get("category"),
                    "description": display_description,
                    "price": display_price,
                    "sku": product.get("sku"),
                    "stock_status": product.get("stock_status"),
                    "permalink": product.get("permalink"),
                }
            )
        return out

    @staticmethod
    def _build_message(intent: str, language: str, fallback: str) -> str:
        """Pick a localised reply for the successful product path."""
        templates = _MESSAGE_TEMPLATES.get(language, _MESSAGE_TEMPLATES["pl"])
        return templates.get(fallback, templates["intent"])

    def _select_products(
        self,
        *,
        message: str,
        intent: str,
        confidence: float,
        language: str,
    ) -> tuple[list[dict], str, str]:
        """Pick the product set and report which fallback path was used.

        Returns ``(products, fallback_label, final_intent)``.
        """
        low_confidence = (
            intent == DEFAULT_INTENT
            or confidence < SETTINGS.confidence_threshold
        )

        if low_confidence:
            fuzzy_matches = self._matcher.search(message, limit=3)
            if fuzzy_matches:
                products = self._build_products_payload(
                    [m.product for m in fuzzy_matches],
                    language,
                )
                final_intent = (
                    fuzzy_matches[0].product.get("category") or DEFAULT_INTENT
                )
                return products, "fuzzy", final_intent
            return [], "default", DEFAULT_INTENT

        products = self._build_products_payload(
            self._fetcher.by_intent(intent),
            language,
        )
        return products, "intent", intent
