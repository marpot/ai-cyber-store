"""WooCommerce product fetcher with in-process TTL cache.

The recommendation service normally hydrates its responses with real
products pulled from the WordPress + WooCommerce REST API. We cache
results for ``product_cache_ttl_seconds`` to avoid hammering WP on every
chat turn. When WP is unreachable (e.g. during local dev or in CI) we
fall back to ``static_products.json`` shipped with the service.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

import httpx

from .config import SETTINGS

logger = logging.getLogger(__name__)


class ProductFetcher:
    def __init__(
        self,
        base_url: str | None = None,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
        cache_ttl: int | None = None,
        static_path: Path | None = None,
        timeout: float = 4.0,
    ) -> None:
        self.base_url = (base_url or SETTINGS.wordpress_api_url).rstrip("/")
        self.consumer_key = consumer_key or SETTINGS.wordpress_consumer_key
        self.consumer_secret = consumer_secret or SETTINGS.wordpress_consumer_secret
        self.cache_ttl = cache_ttl if cache_ttl is not None else SETTINGS.product_cache_ttl_seconds
        self.static_path = static_path or SETTINGS.static_products_path
        self.timeout = timeout

        self._cache: list[dict[str, Any]] = []
        self._fetched_at: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_all(self, *, force_refresh: bool = False) -> list[dict[str, Any]]:
        if not force_refresh and self._is_cache_fresh():
            return self._cache

        products = self._fetch_remote()
        if not products:
            products = self._load_static()
        self._cache = products
        self._fetched_at = time.monotonic()
        return products

    def by_intent(self, intent: str) -> list[dict[str, Any]]:
        return [p for p in self.get_all() if p.get("category") == intent]

    def search(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        """Naive substring fallback used when fuzzy ranking is not enabled."""
        if not query or not query.strip():
            return []
        lowered = query.lower()
        matches = []
        for product in self.get_all():
            haystack = " ".join(
                str(product.get(field, "")) for field in ("name", "name_pl", "description", "description_pl")
            ).lower()
            if lowered in haystack:
                matches.append(product)
            if len(matches) >= limit:
                break
        return matches

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _is_cache_fresh(self) -> bool:
        return bool(self._cache) and (time.monotonic() - self._fetched_at) < self.cache_ttl

    def _fetch_remote(self) -> list[dict[str, Any]]:
        # The Store API is public and is the same catalogue endpoint used by
        # the React storefront. Local development therefore works without
        # creating WooCommerce REST API credentials.
        url = f"{self.base_url}/wp-json/wc/store/v1/products"
        params: dict[str, Any] = {"per_page": 50}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
        except (httpx.HTTPError, httpx.RequestError) as exc:
            logger.warning("WooCommerce fetch failed (%s); using static catalogue", exc)
            return []

        try:
            payload = response.json()
        except json.JSONDecodeError:
            logger.warning("WooCommerce returned non-JSON payload; using static catalogue")
            return []

        return [self._normalise_remote(item) for item in payload]

    def _normalise_remote(self, item: dict[str, Any]) -> dict[str, Any]:
        categories = item.get("categories") or []
        category_slug = _intent_for_product(item, categories)
        prices = item.get("prices") or {}
        price = _format_store_price(prices)
        search_terms = _store_attribute_terms(item.get("attributes") or [])
        return {
            "id": item.get("id"),
            "name": item.get("name", ""),
            "name_pl": item.get("name", ""),
            "category": category_slug,
            "price": price,
            "price_pl": price,
            "description": _strip_html(item.get("description", "")),
            "description_pl": _strip_html(item.get("description", "")),
            "search_text": search_terms,
            "sku": item.get("sku", ""),
            "stock_status": item.get("stock_status", "instock"),
            "permalink": item.get("permalink", ""),
        }

    def _load_static(self) -> list[dict[str, Any]]:
        path = self.static_path
        if not path.exists():
            logger.warning("Static product catalogue not found at %s", path)
            return []
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)


def _strip_html(value: str) -> str:
    """Very small HTML stripper — avoids pulling in BeautifulSoup for one call."""
    if not value:
        return ""
    out = []
    in_tag = False
    for ch in value:
        if ch == "<":
            in_tag = True
        elif ch == ">":
            in_tag = False
        elif not in_tag:
            out.append(ch)
    return "".join(out).strip()


_SLUG_INTENTS = {
    "safetunnel-vpn": "network_security",
    "vaultpass-password-manager": "password_security",
    "titankey-hardware-security-key": "password_security",
    "sentinel-endpoint-protection": "malware_protection",
    "cybersafe-cloud-backup": "device_security",
}


def _intent_for_product(
    item: dict[str, Any],
    categories: list[dict[str, Any]],
) -> str:
    slug = str(item.get("slug", ""))
    if slug in _SLUG_INTENTS:
        return _SLUG_INTENTS[slug]

    category_slug = categories[0].get("slug") if categories else "general_query"
    return str(category_slug).replace("-", "_")


def _format_store_price(prices: dict[str, Any]) -> str:
    raw_price = str(prices.get("price", ""))
    if not raw_price:
        return ""

    minor_units = int(prices.get("currency_minor_unit", 2))
    symbol = str(prices.get("currency_symbol", "")).strip()
    amount = int(raw_price) / (10 ** minor_units)
    return f"{amount:.{minor_units}f} {symbol}".strip()


def _store_attribute_terms(attributes: list[dict[str, Any]]) -> str:
    terms: list[str] = []
    for attribute in attributes:
        for term in attribute.get("terms") or []:
            name = str(term.get("name", "")).strip()
            if name:
                terms.append(name)
    return " ".join(terms)
