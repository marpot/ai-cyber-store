"""Fuzzy product matching for free-text user queries.

Used as a fallback when the intent classifier returns a generic
``general_query`` or low-confidence result. Scores are produced by
``rapidfuzz`` against product name + description fields in both Polish
and English.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from rapidfuzz import fuzz, process

from .products import ProductFetcher


@dataclass(frozen=True)
class FuzzyMatch:
    product: dict
    score: float


class FuzzyMatcher:
    def __init__(self, fetcher: ProductFetcher | None = None) -> None:
        self.fetcher = fetcher or ProductFetcher()

    def search(self, query: str, *, limit: int = 3, min_score: float = 30.0) -> list[FuzzyMatch]:
        if not query or not query.strip():
            return []
        products = self.fetcher.get_all()
        if not products:
            return []

        # Cheap keyword pre-filter: if the query contains a known category
        # hint word, restrict the candidate pool to that category. This
        # avoids the fuzzy ranker scoring e.g. "antywirus" highest against
        # "Uwierzytelnianie Dwuskładnikowe" just because of edit distance.
        HINT_TO_CATEGORY = {
            "antywirus": "malware_protection",
            "antivirus": "malware_protection",
            "virus": "malware_protection",
            "malware": "malware_protection",
            "trojan": "malware_protection",
            "ransomware": "malware_protection",
            "wifi": "network_security",
            "router": "network_security",
            "network": "network_security",
            "sieć": "network_security",
            "router": "network_security",
            "laptop": "device_security",
            "komputer": "device_security",
            "computer": "device_security",
            "telefon": "device_security",
            "phone": "device_security",
            "mobile": "device_security",
            "hasło": "password_security",
            "hasła": "password_security",
            "password": "password_security",
            "2fa": "password_security",
            "vpn": "privacy",
            "prywatność": "privacy",
            "privacy": "privacy",
        }
        lowered = query.lower()
        category_hint = None
        for hint, category in HINT_TO_CATEGORY.items():
            if hint in lowered:
                category_hint = category
                break
        if category_hint:
            products = [p for p in products if p.get("category") == category_hint] or products

        choices: dict[str, dict] = {}
        for product in products:
            for field in ("name", "name_pl", "description", "description_pl"):
                value = str(product.get(field) or "").strip()
                if value:
                    choices[value] = product

        if not choices:
            return []

        ranked = process.extract(
            query,
            choices.keys(),
            scorer=fuzz.WRatio,
            limit=limit * 3,  # over-fetch to dedupe on product id
        )

        seen: set[Any] = set()
        results: list[FuzzyMatch] = []
        for text, score, _key in ranked:
            if score < min_score:
                continue
            product = choices[text]
            pid = product.get("id")
            if pid in seen:
                continue
            seen.add(pid)
            results.append(FuzzyMatch(product=product, score=score / 100.0))
            if len(results) >= limit:
                break
        return results

    @staticmethod
    def to_payload(matches: Iterable[FuzzyMatch], language: str = "pl") -> list[dict]:
        out: list[dict] = []
        for match in matches:
            product = dict(match.product)
            # Re-localise name/description/price based on language.
            if language == "en":
                product["display_name"] = product.get("name") or product.get("name_pl")
                product["display_description"] = product.get("description") or product.get("description_pl")
                product["display_price"] = product.get("price") or product.get("price_pl")
            else:
                product["display_name"] = product.get("name_pl") or product.get("name")
                product["display_description"] = product.get("description_pl") or product.get("description")
                product["display_price"] = product.get("price_pl") or product.get("price")
            product["match_score"] = round(match.score, 3)
            out.append(product)
        return out