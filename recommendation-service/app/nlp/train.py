"""Compatibility shim for legacy imports.

The historical training entry point was `nlp.train.train_model`. The
real implementation lives in ``app.nlp.predict.train_model``; this
module re-exports it so existing scripts keep working.
"""
from .predict import train_model  # noqa: F401