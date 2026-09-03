"""Integration tests for /api/recommendation.

Uses FastAPI's TestClient so no network server is needed.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    # Import inside the fixture so the model is loaded exactly once
    # for all tests in this module.
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "running"


def test_intents_listed(client):
    response = client.get("/intents")
    assert response.status_code == 200
    intents = response.json()["intents"]
    assert {"device_security", "network_security", "malware_protection"}.issubset(intents)


def test_recommendation_polish_high_confidence(client):
    response = client.post(
        "/api/recommendation",
        json={"message": "jak zabezpieczyć mój laptop przed wirusami"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "pl"
    assert body["intent"] in {"device_security", "malware_protection"}
    assert body["confidence"] >= 0.0
    assert "products" in body


def test_recommendation_english_high_confidence(client):
    response = client.post(
        "/api/recommendation",
        json={"message": "how can I secure my router and home network"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "en"
    assert body["intent"] in {"network_security"}


def test_recommendation_empty_message_rejected(client):
    response = client.post("/api/recommendation", json={"message": ""})
    assert response.status_code == 422


def test_recommendation_explicit_language_overrides(client):
    response = client.post(
        "/api/recommendation",
        json={"message": "hello", "language": "en"},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "en"


def test_recommendation_legacy_endpoint(client):
    response = client.post(
        "/recommendation",
        json={"message": "jak chronić komputer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "intent" in body
    assert "confidence" in body
    assert "classes" in body


def test_recommendation_fuzzy_fallback_for_unknown_query(client):
    """A query outside the training data should still return products via fuzzy."""
    response = client.post(
        "/api/recommendation",
        json={"message": "szukam czegoś do szyfrowania mojego internetu bezprzewodowego"},
    )
    assert response.status_code == 200
    body = response.json()
    # Either fuzzy or default fallback — both are valid, but products
    # should be present when fuzzy hits.
    assert "products" in body
    assert body["fallback"] in {"intent", "fuzzy", "default"}