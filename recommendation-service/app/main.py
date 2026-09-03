"""FastAPI entry point for the AI Cybersecurity Store recommendation API.

This module is intentionally a thin HTTP layer:

    1. configure the app,
    2. wire up shared resources on ``app.state``,
    3. define endpoints,
    4. delegate the recommendation pipeline to
       :class:`app.services.recommendation.RecommendationService`.

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

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import SETTINGS
from .fuzzy import FuzzyMatcher
from .nlp.predict import ALLOWED_INTENTS, predict_intent
from .products import ProductFetcher
from .schemas import RecommendationRequest
from .services.recommendation import RecommendationService

logger = logging.getLogger(__name__)


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

    fetcher: ProductFetcher = app.state.product_fetcher
    try:
        fetcher.get_all(force_refresh=True)
        logger.info(
            "Product catalogue warmed up (%d items)", len(fetcher.get_all())
        )
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


# Shared, long-lived resources.
app.state.product_fetcher = ProductFetcher()
app.state.fuzzy_matcher = FuzzyMatcher(app.state.product_fetcher)
app.state.recommendation_service = RecommendationService(
    fetcher=app.state.product_fetcher,
    matcher=app.state.fuzzy_matcher,
)


def get_recommendation_service(request: Request) -> RecommendationService:
    """Resolve the shared service instance from ``app.state``."""
    return request.app.state.recommendation_service


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


@app.post("/api/recommendation")
def get_recommendation(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> dict:
    return service.recommend(
        message=request.message,
        explicit_language=request.language,
    )


@app.post("/recommendation")
def get_recommendation_legacy(request: RecommendationRequest) -> dict:
    intent, confidence, classes = predict_intent(request.message)
    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "classes": classes,
    }
