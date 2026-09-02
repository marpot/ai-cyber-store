"""Lazy-loaded intent classifier.

The model is loaded on first call rather than at import time so that
tests can monkeypatch the model path or skip loading entirely.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from ..config import SETTINGS

logger = logging.getLogger(__name__)

ALLOWED_INTENTS = {
    "device_security",
    "network_security",
    "malware_protection",
    "password_security",
    "privacy",
    "general_query",
}

DEFAULT_INTENT = "general_query"


def create_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            (
                "classifier",
                LogisticRegression(max_iter=2000, class_weight="balanced"),
            ),
        ]
    )


def train_model(model_path: Path | None = None, dataset_path: Path | None = None) -> Pipeline:
    """Train + persist a fresh model. Returns the fitted pipeline."""
    from .dataset import load_dataset  # local to avoid hard import at module load

    df = pd.read_csv(dataset_path or Path(__file__).parent / "data" / "intents.csv")
    if df.isnull().any().any():
        raise ValueError("Dataset contains missing values")
    df = df.dropna(subset=["text", "intent"]).reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["intent"],
        test_size=0.2,
        random_state=42,
        stratify=df["intent"],
    )

    model = create_model()
    model.fit(X_train, y_train)
    target = model_path or SETTINGS.model_path
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, target)
    logger.info("Model saved to %s", target)
    return model


@lru_cache(maxsize=1)
def get_model() -> Any:
    """Load (and cache) the trained model from disk.

    Raises FileNotFoundError if the model hasn't been trained yet — the
    caller (FastAPI startup event) is expected to trigger ``train_model``
    in development.
    """
    path = SETTINGS.model_path
    if not path.exists():
        logger.info("Model not found at %s — training now", path)
        return train_model(model_path=path)
    return joblib.load(path)


def predict_intent(text: str) -> tuple[str, float, list[str]]:
    """Predict intent for a single message.

    Returns ``(intent, confidence, classes)``. ``confidence`` is the max
    class probability in the [0.0, 1.0] range. ``classes`` is the list
    of intent labels known by the model in the same order as
    ``predict_proba``.
    """
    if not text or not text.strip():
        return DEFAULT_INTENT, 0.0, list(ALLOWED_INTENTS)

    model = get_model()
    probabilities = model.predict_proba([text])[0]
    classes = list(model.classes_)
    top_idx = int(probabilities.argmax())
    intent = str(classes[top_idx])
    if intent not in ALLOWED_INTENTS:
        intent = DEFAULT_INTENT
    return intent, float(probabilities[top_idx]), classes


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    train_model()
    for sample in [
        "jak zabezpieczyć moje wifi",
        "chcę ochronić router",
        "mam wirusa",
        "help me pick a password",
    ]:
        intent, confidence, _ = predict_intent(sample)
        print(f"{sample!r} -> {intent} ({confidence:.2f})")