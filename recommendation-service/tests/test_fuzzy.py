from app.fuzzy import FuzzyMatcher
from app.products import ProductFetcher


def test_fuzzy_matches_polish_phrase():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    matches = matcher.search("potrzebuję programu antywirusowego", limit=3, min_score=40)
    assert matches, "expected fuzzy match for Polish antivirus phrase"
    assert all(m.score <= 1.0 for m in matches)


def test_fuzzy_matches_english_phrase():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    matches = matcher.search("wifi encryption", limit=3, min_score=40)
    assert matches


def test_fuzzy_returns_unique_products():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    matches = matcher.search("vpn privacy", limit=5, min_score=30)
    ids = [m.product["id"] for m in matches]
    assert len(ids) == len(set(ids))


def test_fuzzy_empty_query():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    assert matcher.search("") == []
    assert matcher.search("   ") == []


def test_fuzzy_to_payload_polish():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    matches = matcher.search("antywirus", limit=2, min_score=40)
    payload = FuzzyMatcher.to_payload(matches, language="pl")
    assert payload
    for item in payload:
        assert "display_name" in item
        assert "match_score" in item


def test_fuzzy_to_payload_english():
    fetcher = ProductFetcher()
    matcher = FuzzyMatcher(fetcher)
    matches = matcher.search("antivirus", limit=2, min_score=40)
    payload = FuzzyMatcher.to_payload(matches, language="en")
    assert payload
    for item in payload:
        # English fallback uses *non-empty* display fields.
        assert item["display_name"]