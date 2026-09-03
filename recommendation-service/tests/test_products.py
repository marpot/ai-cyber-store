from app.products import ProductFetcher


def test_static_catalogue_loads():
    fetcher = ProductFetcher()
    products = fetcher.get_all(force_refresh=True)
    assert len(products) >= 6
    for product in products:
        assert {"id", "name", "name_pl", "category", "price", "price_pl"}.issubset(
            product.keys()
        )


def test_by_intent_filters_correctly():
    fetcher = ProductFetcher()
    fetcher.get_all(force_refresh=True)
    network = fetcher.by_intent("network_security")
    assert network
    assert all(p["category"] == "network_security" for p in network)


def test_search_substring_match():
    fetcher = ProductFetcher()
    fetcher.get_all(force_refresh=True)
    results = fetcher.search("VPN")
    assert results
    assert any("vpn" in (p.get("name_pl", "") + p.get("name", "")).lower() for p in results)


def test_search_empty_returns_empty():
    fetcher = ProductFetcher()
    assert fetcher.search("") == []


def test_caching_avoids_refetch():
    fetcher = ProductFetcher()
    first = fetcher.get_all()
    second = fetcher.get_all()
    assert first is second