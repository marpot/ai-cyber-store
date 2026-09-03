"""Fuzzy product matching for free-text user queries.

This module provides a robust fallback product matcher for cases where
the intent classifier returns ``general_query`` or a low-confidence result.

Matching combines:
- text normalization,
- category hints,
- product-name matching,
- description matching,
- Polish/English synonyms,
- weighted fuzzy scores.

The matcher is intentionally deterministic and explainable so that
recommendation results can be inspected and debugged easily.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata
from typing import Any, Iterable

from rapidfuzz import fuzz

from .products import ProductFetcher


@dataclass(frozen=True)
class FuzzyMatch:
    """A product matched against a user query."""

    product: dict
    score: float
    matched_field: str


class FuzzyMatcher:
    """Find products that are semantically close to a free-text query."""

    # Words/phrases that strongly indicate a product category.
    HINT_TO_CATEGORY: dict[str, str] = {
        # Malware
        "antywirus": "malware_protection",
        "antywirusowy": "malware_protection",
        "antivirus": "malware_protection",
        "antivirusowy": "malware_protection",
        "virus": "malware_protection",
        "wirus": "malware_protection",
        "wirusami": "malware_protection",
        "malware": "malware_protection",
        "trojan": "malware_protection",
        "ransomware": "malware_protection",

        # Network
        "wifi": "network_security",
        "wi-fi": "network_security",
        "router": "network_security",
        "network": "network_security",
        "sieć": "network_security",
        "siec": "network_security",
        "sieci": "network_security",

        # Device
        "laptop": "device_security",
        "komputer": "device_security",
        "computer": "device_security",
        "pc": "device_security",
        "telefon": "device_security",
        "telefonie": "device_security",
        "phone": "device_security",
        "mobile": "device_security",

        # Passwords / authentication
        "hasło": "password_security",
        "hasla": "password_security",
        "hasła": "password_security",
        "password": "password_security",
        "2fa": "password_security",
        "mfa": "password_security",
        "uwierzytelnianie": "password_security",
        "autoryzacja": "password_security",

        # Privacy
        "vpn": "privacy",
        "prywatność": "privacy",
        "prywatnosc": "privacy",
        "privacy": "privacy",
    }

    # Common Polish/English variations.
    SYNONYMS: dict[str, tuple[str, ...]] = {
        "antywirus": (
            "antywirus",
            "antivirus",
            "ochrona wirusów",
            "ochrona przed wirusami",
            "virus protection",
        ),
        "vpn": (
            "vpn",
            "prywatność",
            "privacy",
            "bezpieczne połączenie",
            "secure connection",
        ),
        "hasło": (
            "hasło",
            "hasła",
            "password",
            "passwords",
            "logowanie",
            "login",
        ),
        "wifi": (
            "wifi",
            "wi-fi",
            "sieć",
            "siec",
            "network",
            "router",
        ),
        "ransomware": (
            "ransomware",
            "wymuszenie okupu",
            "atak ransomware",
        ),
    }

    def __init__(self, fetcher: ProductFetcher | None = None) -> None:
        self.fetcher = fetcher or ProductFetcher()

    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for more reliable fuzzy matching.

        - lowercases,
        - strips Polish/Unicode diacritics via NFKD,
        - removes punctuation,
        - collapses whitespace.
        """
        text = text.lower().strip()

        # Replace Polish/Unicode characters with their base characters.
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            char
            for char in text
            if not unicodedata.combining(char)
        )

        # Normalize punctuation and whitespace.
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def _detect_categories(cls, query: str) -> set[str]:
        """Return all categories suggested by the query.

        Uses substring matching against the lowered, diacritics-stripped
        query so that Polish inflections like "antywirusowego" still
        trigger the malware_protection category.
        """
        normalized = cls._normalize(query)

        categories: set[str] = set()

        for hint, category in cls.HINT_TO_CATEGORY.items():
            normalized_hint = cls._normalize(hint)
            if normalized_hint and normalized_hint in normalized:
                categories.add(category)

        return categories

    @classmethod
    def _expand_query(cls, query: str) -> str:
        """Add known synonyms to improve matching."""

        normalized = cls._normalize(query)
        expanded = [normalized]

        for key, synonyms in cls.SYNONYMS.items():
            normalized_key = cls._normalize(key)

            if normalized_key in normalized:
                expanded.extend(
                    cls._normalize(synonym)
                    for synonym in synonyms
                )

        return " ".join(dict.fromkeys(expanded))

    @staticmethod
    def _score_product(query: str, product: dict) -> tuple[float, str]:
        """Calculate a weighted score for one product."""

        query_normalized = FuzzyMatcher._normalize(query)

        fields = {
            "name": FuzzyMatcher._normalize(
                str(product.get("name") or "")
            ),
            "name_pl": FuzzyMatcher._normalize(
                str(product.get("name_pl") or "")
            ),
            "description": FuzzyMatcher._normalize(
                str(product.get("description") or "")
            ),
            "description_pl": FuzzyMatcher._normalize(
                str(product.get("description_pl") or "")
            ),
        }

        # Product names are much more important than descriptions.
        name_scores = [
            fuzz.WRatio(query_normalized, fields["name"])
            if fields["name"]
            else 0,
            fuzz.WRatio(query_normalized, fields["name_pl"])
            if fields["name_pl"]
            else 0,
        ]

        description_scores = [
            fuzz.token_set_ratio(
                query_normalized,
                fields["description"],
            )
            if fields["description"]
            else 0,
            fuzz.token_set_ratio(
                query_normalized,
                fields["description_pl"],
            )
            if fields["description_pl"]
            else 0,
        ]

        best_name_score = max(name_scores, default=0)
        best_description_score = max(description_scores, default=0)

        # Name has a stronger influence than description.
        final_score = (
            best_name_score * 0.70
            + best_description_score * 0.30
        )

        matched_field = (
            "name"
            if best_name_score >= best_description_score
            else "description"
        )

        return final_score, matched_field

    def search(
        self,
        query: str,
        *,
        limit: int = 3,
        min_score: float = 30.0,
    ) -> list[FuzzyMatch]:
        """Search products using weighted fuzzy matching.

        Returns at most ``limit`` matches with score >= ``min_score``
        (0-100 scale). Results are ordered by score (descending) and
        deduplicated by product id.
        """

        if not query or not query.strip():
            return []

        if limit <= 0:
            return []

        products = self.fetcher.get_all()

        if not products:
            return []

        normalized_query = self._normalize(query)
        expanded_query = self._expand_query(query)

        categories = self._detect_categories(query)

        # Prefer products from detected categories.
        if categories:
            filtered_products = [
                product
                for product in products
                if product.get("category") in categories
            ]

            # Never return an empty result just because the category
            # detector was too restrictive.
            if filtered_products:
                products = filtered_products

        scored_products: list[FuzzyMatch] = []

        for product in products:
            # Score against the original query.
            original_score, matched_field = self._score_product(
                normalized_query,
                product,
            )

            # Score against expanded synonyms.
            expanded_score, _ = self._score_product(
                expanded_query,
                product,
            )

            # Give the original query slightly more weight.
            final_score = (
                original_score * 0.75
                + expanded_score * 0.25
            )

            if final_score < min_score:
                continue

            scored_products.append(
                FuzzyMatch(
                    product=product,
                    score=final_score / 100.0,
                    matched_field=matched_field,
                )
            )

        # Highest score first.
        scored_products.sort(
            key=lambda match: match.score,
            reverse=True,
        )

        # Deduplicate products.
        results: list[FuzzyMatch] = []
        seen_ids: set[Any] = set()

        for match in scored_products:
            product_id = match.product.get("id")

            if product_id in seen_ids:
                continue

            seen_ids.add(product_id)
            results.append(match)

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def to_payload(
        matches: Iterable[FuzzyMatch],
        language: str = "pl",
    ) -> list[dict]:
        """Convert fuzzy matches into API-friendly dictionaries."""

        output: list[dict] = []

        for match in matches:
            product = dict(match.product)

            if language == "en":
                display_name = (
                    product.get("name")
                    if product.get("name") is not None
                    else product.get("name_pl")
                )

                display_description = (
                    product.get("description")
                    if product.get("description") is not None
                    else product.get("description_pl")
                )

                display_price = (
                    product.get("price")
                    if product.get("price") is not None
                    else product.get("price_pl")
                )

            else:
                display_name = (
                    product.get("name_pl")
                    if product.get("name_pl") is not None
                    else product.get("name")
                )

                display_description = (
                    product.get("description_pl")
                    if product.get("description_pl") is not None
                    else product.get("description")
                )

                display_price = (
                    product.get("price_pl")
                    if product.get("price_pl") is not None
                    else product.get("price")
                )

            product["display_name"] = display_name
            product["display_description"] = display_description
            product["display_price"] = display_price

            product["match_score"] = round(match.score, 3)
            product["matched_field"] = match.matched_field

            output.append(product)

        return output
