"""Pytest fixtures shared across the recommendation-service tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SERVICE_ROOT = Path(__file__).resolve().parent.parent
APP_ROOT = SERVICE_ROOT / "app"

# Make `app.*` imports work without installing the package.
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))


@pytest.fixture(scope="session")
def service_root() -> Path:
    return SERVICE_ROOT


@pytest.fixture(scope="session")
def dataset_path() -> Path:
    return APP_ROOT / "nlp" / "data" / "intents.csv"