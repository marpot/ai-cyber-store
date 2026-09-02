"""Dataset loader used by both ``nlp.predict.train_model`` and the
pytest suite. Kept tiny on purpose — pandas does the heavy lifting.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

DATASET_PATH = Path(__file__).parent / "data" / "intents.csv"


def load_dataset(path: Path | None = None):
    df = pd.read_csv(path or DATASET_PATH)
    df = df.dropna(subset=["text", "intent"]).reset_index(drop=True)
    X = df["text"]
    y = df["intent"]
    return X, y, df


def validate_dataset(path: Path | None = None) -> None:
    """Raise ValueError on dataset issues. Useful in tests and CI."""
    df = pd.read_csv(path or DATASET_PATH)
    required = {"text", "intent", "language"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
    if df.isnull().any().any():
        raise ValueError("Dataset contains NaN values")
    if (df["text"].str.strip() == "").any():
        raise ValueError("Dataset contains empty text rows")
    duplicates = df[df.duplicated(subset=["text"], keep=False)]
    if not duplicates.empty:
        raise ValueError(
            f"Dataset contains duplicate texts: {duplicates['text'].tolist()[:5]}"
        )