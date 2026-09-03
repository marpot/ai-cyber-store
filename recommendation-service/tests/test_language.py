from app.language import detect_language


def test_polish_detection_basic():
    assert detect_language("jak zabezpieczyć moje wifi") == "pl"


def test_english_detection_basic():
    assert detect_language("how can I protect my laptop") == "en"


def test_empty_text_returns_unknown():
    assert detect_language("") == "unknown"
    assert detect_language("   ") == "unknown"


def test_diacritics_strong_signal_polish():
    # Diacritics should win over English hint words.
    assert detect_language("łódź") == "pl"


def test_caching_returns_same_result():
    detect_language.cache_clear()
    first = detect_language("jak chronić komputer")
    second = detect_language("jak chronić komputer")
    assert first == second == "pl"