"""Pydantic schemas exposed by the HTTP layer.

Kept in a dedicated module so both ``main.py`` (request parsing) and
``services/recommendation.py`` (response building) can share a single
source of truth for the wire contract.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Body accepted by ``POST /api/recommendation`` and ``POST /recommendation``."""

    message: str = Field(..., min_length=1, max_length=1000)
    language: Optional[str] = Field(default=None, description="pl|en|auto")


class RecommendationResponse(BaseModel):
    """Shape of the JSON returned by ``POST /api/recommendation``.

    Field names match the existing front/back-end contract exactly.
    """

    intent: str
    confidence: float
    language: str
    message: str
    products: list[dict]
    fallback: str
