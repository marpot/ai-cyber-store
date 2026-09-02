"""FastAPI entry point for the AI Cybersecurity Store recommendation API.

Endpoints:
- GET  /                          liveness banner
- GET  /health                    health probe (used by docker-compose)
- GET  /intents                   list of intents the model knows about
- POST /api/recommendation        main chat endpoint
- POST /recommendation            legacy endpoint kept for backwards compat
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import SETTINGS
from .fuzzy import FuzzyMatcher
from .language import detect_language
from .nlp.predict import ALLOWED_INTENTS, DEFAULT_INTENT, predict_intent
from .products import ProductFetcher

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Default fallback messages (localised) — used when the model has low
# confidence and the fuzzy fallback also produced nothing useful.
# ----------------------------------------------------------------------
DEFAULT_RESPONSES = {
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up the model and the product cache at startup so the first
    user-facing request doesn't pay the training cost.
    """
    logging.basicConfig(level=logging.INFO)
    try:
        from .nlp.predict import get_model

        get_model()
        logger.info("Intent model ready")
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to load intent model: %s", exc)

    fetcher = getattr(app.state, "product_fetcher", None)
    if fetcher is not None:
        try:
            fetcher.get_all(force_refresh=True)
            logger.info("Product catalogue warmed up (%d items)", len(fetcher.get_all()))
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to warm product cache: %s", exc)

    yield


app = FastAPI(
    title="AI Cybersecurity Store API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.cors_allow_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.product_fetcher = ProductFetcher()
app.state.fuzzy_matcher = FuzzyMatcher(app.state.product_fetcher)


# ----------------------------------------------------------------------
# Schemas
# ----------------------------------------------------------------------
class RecommendationRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(default=None, description="pl|en|auto")


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------
@app.get("/")
def home() -> dict:
    return {
        "service": "AI Cybersecurity Store API",
        "version": app.version,
        "status": "running",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/intents")
def list_intents() -> dict:
    return {"intents": sorted(ALLOWED_INTENTS)}


def _pick_language(explicit: Optional[str], fallback_text: str) -> str:
    if explicit and explicit.lower() in {"pl", "en"}:
        return explicit.lower()
    detected = detect_language(fallback_text)
    if detected in {"pl", "en"}:
        return detected
    return "pl"


def _build_products_payload(products: list[dict], language: str) -> list[dict]:
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


@app.post("/api/recommendation")
def get_recommendation(request: RecommendationRequest) -> dict:
    language = _pick_language(request.language, request.message)
    intent, confidence, _classes = predict_intent(request.message)

    fetcher: ProductFetcher = app.state.product_fetcher
    matcher: FuzzyMatcher = app.state.fuzzy_matcher

    products: list[dict] = []
    fallback = "intent"

    if intent == DEFAULT_INTENT or confidence < SETTINGS.confidence_threshold:
        fuzzy_matches = matcher.search(request.message, limit=3)
        if fuzzy_matches:
            products = _build_products_payload(
                [m.product for m in fuzzy_matches], language
            )
            fallback = "fuzzy"
            intent = fuzzy_matches[0].product.get("category", DEFAULT_INTENT)
        else:
            fallback = "default"
            intent = DEFAULT_INTENT
    else:
        products = _build_products_payload(fetcher.by_intent(intent), language)

    if not products:
        # Last resort — surface the default help message.
        default = DEFAULT_RESPONSES.get(language, DEFAULT_RESPONSES["pl"])
        return {
            "intent": intent,
            "confidence": round(confidence, 3),
            "language": language,
            "message": default["message"],
            "products": [],
            "fallback": "default",
        }

    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "language": language,
        "message": _build_message(intent, language, fallback),
        "products": products,
        "fallback": fallback,
    }


def _build_message(intent: str, language: str, fallback: str) -> str:
    templates = {
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
    return templates.get(language, templates["pl"]).get(
        fallback, templates[language]["intent"]
    )


# ----------------------------------------------------------------------
# Legacy endpoint — kept for backwards compatibility.
# ----------------------------------------------------------------------
@app.post("/recommendation")
def get_recommendation_legacy(request: RecommendationRequest) -> dict:
    intent, confidence, classes = predict_intent(request.message)
    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "classes": classes,
    }