from app.fuzzy import FuzzyMatcher
from app.products import ProductFetcher


def _matcher() -> FuzzyMatcher:
    return FuzzyMatcher(ProductFetcher())


# ----------------------------------------------------------------------
# Functional / behavioural cases (carried over from the original suite)
# ----------------------------------------------------------------------
def test_fuzzy_matches_polish_phrase():
    matcher = _matcher()
    matches = matcher.search(
        "potrzebuję programu antywirusowego", limit=3, min_score=30
    )
    assert matches, "expected fuzzy match for Polish antivirus phrase"
    assert all(m.score <= 1.0 for m in matches)
    assert all(m.product.get("category") == "malware_protection" for m in matches)


def test_fuzzy_matches_english_phrase():
    matcher = _matcher()
    matches = matcher.search("wifi encryption", limit=3, min_score=40)
    assert matches


def test_fuzzy_returns_unique_products():
    matcher = _matcher()
    matches = matcher.search("vpn privacy", limit=5, min_score=30)
    ids = [m.product["id"] for m in matches]
    assert len(ids) == len(set(ids))


def test_fuzzy_empty_query():
    matcher = _matcher()
    assert matcher.search("") == []
    assert matcher.search("   ") == []


def test_fuzzy_to_payload_polish():
    matcher = _matcher()
    matches = matcher.search("antywirus", limit=2, min_score=40)
    payload = FuzzyMatcher.to_payload(matches, language="pl")
    assert payload
    for item in payload:
        assert "display_name" in item
        assert "match_score" in item


def test_fuzzy_to_payload_english():
    matcher = _matcher()
    matches = matcher.search("antivirus", limit=2, min_score=40)
    payload = FuzzyMatcher.to_payload(matches, language="en")
    assert payload
    for item in payload:
        assert item["display_name"]


# ----------------------------------------------------------------------
# New edge cases — limit / min_score / category filter
# ----------------------------------------------------------------------
def test_fuzzy_respects_limit():
    matcher = _matcher()
    matches = matcher.search("security", limit=2, min_score=20)
    assert len(matches) <= 2


def test_fuzzy_limit_zero_returns_empty():
    matcher = _matcher()
    assert matcher.search("antywirus", limit=0, min_score=0) == []


def test_fuzzy_min_score_filters_out_low_scores():
    matcher = _matcher()
    # A very high threshold should drop almost everything.
    matches = matcher.search("xyzqwerty nonsense", limit=5, min_score=99)
    assert matches == []


def test_fuzzy_category_hint_filter():
    """The wifi hint must steer results to network_security only."""
    matcher = _matcher()
    matches = matcher.search("wifi router", limit=5, min_score=30)
    if matches:
        assert all(m.product.get("category") == "network_security" for m in matches)


def test_fuzzy_dedup_when_categories_match_multiple_fields():
    matcher = _matcher()
    matches = matcher.search("vpn", limit=10, min_score=30)
    ids = [m.product["id"] for m in matches]
    assert len(ids) == len(set(ids))


def test_fuzzy_score_in_zero_one_range():
    matcher = _matcher()
    matches = matcher.search("antywirus", limit=5, min_score=30)
    for match in matches:
        assert 0.0 <= match.score <= 1.0
        assert match.matched_field in {"name", "description"}
