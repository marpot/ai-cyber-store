import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def reset_settings_cache():
    """Each test sees a fresh Settings object even if env was patched."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_default_threshold(monkeypatch):
    monkeypatch.delenv("RECOMMENDATION_CONFIDENCE_THRESHOLD", raising=False)
    s = get_settings()
    assert 0.0 <= s.confidence_threshold <= 1.0


def test_settings_threshold_from_env(monkeypatch):
    monkeypatch.setenv("RECOMMENDATION_CONFIDENCE_THRESHOLD", "0.73")
    s = get_settings()
    assert s.confidence_threshold == 0.73


def test_settings_invalid_threshold_falls_back(monkeypatch):
    monkeypatch.setenv("RECOMMENDATION_CONFIDENCE_THRESHOLD", "not-a-number")
    s = get_settings()
    # Falls back to default 0.45 instead of crashing.
    assert s.confidence_threshold == 0.45


def test_settings_cors_list(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://a.test, http://b.test , http://c.test")
    s = get_settings()
    assert s.cors_allow_origins == ["http://a.test", "http://b.test", "http://c.test"]


def test_settings_model_path_resolves():
    s = get_settings()
    assert s.model_path.suffix == ".joblib"