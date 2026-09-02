from app import llm
from app.config import SETTINGS


def test_llm_disabled_by_default(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    # Force settings reload.
    from app.config import get_settings

    get_settings.cache_clear()
    assert llm.llm_enabled() is False
    assert llm.chat("anything") is None


def test_llm_disabled_with_empty_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()
    assert llm.llm_enabled() is False


def test_llm_enabled_with_key(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    from app.config import get_settings

    get_settings.cache_clear()
    assert llm.llm_enabled() is True