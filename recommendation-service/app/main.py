from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nlp.predict import predict_intent


app = FastAPI(
    title="AI Cybersecurity Store API",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendationRequest(BaseModel):
    message: str
    language: Optional[str] = "pl"


# Product recommendations mapping based on detected intent and language
PRODUCT_RECOMMENDATIONS = {
    "pl": {
        "device_security": {
            "message": "Na podstawie Twojego pytania o ochronę urządzeń, polecam nasze produkty do zabezpieczenia sprzętu:",
            "products": [
                {
                    "id": 1,
                    "name": "Zaawansowany Pakiet Ochrony Urządzeń",
                    "price": "199.99 zł",
                    "category": "device_security",
                    "description": "Kompleksowa ochrona laptopów i komputerów stacjonarnych"
                },
                {
                    "id": 2,
                    "name": "Monitor Zagrożeń w Czasie Rzeczywistym",
                    "price": "119.99 zł",
                    "category": "device_security",
                    "description": "Ciągłe monitorowanie i natychmiastowe wykrywanie zagrożeń"
                }
            ]
        },
        "network_security": {
            "message": "W zakresie bezpieczeństwa sieci i sieci Wi-Fi, sprawdź poniższe rozwiązania:",
            "products": [
                {
                    "id": 3,
                    "name": "Pakiet Ochrony Routera",
                    "price": "319.99 zł",
                    "category": "network_security",
                    "description": "Kompleksowa ochrona routera i całej sieci domowej lub firmowej"
                },
                {
                    "id": 4,
                    "name": "Narzędzie Szyfrowania Wi-Fi",
                    "price": "79.99 zł",
                    "category": "network_security",
                    "description": "Zaawansowane szyfrowanie dla Twojej sieci bezprzewodowej"
                }
            ]
        },
        "malware_protection": {
            "message": "Aby zabezpieczyć się przed złośliwym oprogramowaniem i wirusami, polecam:",
            "products": [
                {
                    "id": 5,
                    "name": "Anti-Malware Pro",
                    "price": "159.99 zł",
                    "category": "malware_protection",
                    "description": "Skuteczne usuwanie złośliwego oprogramowania i wirusów"
                },
                {
                    "id": 6,
                    "name": "Tarcza Przed Malware w Czasie Rzeczywistym",
                    "price": "239.99 zł",
                    "category": "malware_protection",
                    "description": "Ciągła ochrona przed malware i automatyczna kwarantanna"
                }
            ]
        }
    },
    "en": {
        "device_security": {
            "message": "Based on your question about device security, I recommend our device protection products:",
            "products": [
                {
                    "id": 1,
                    "name": "Advanced Device Security Suite",
                    "price": "$49.99",
                    "category": "device_security",
                    "description": "Comprehensive protection for laptops and computers"
                },
                {
                    "id": 2,
                    "name": "Real-time Threat Monitor",
                    "price": "$29.99",
                    "category": "device_security",
                    "description": "Continuous monitoring and threat detection"
                }
            ]
        },
        "network_security": {
            "message": "For network and WiFi security, check out these solutions:",
            "products": [
                {
                    "id": 3,
                    "name": "Router Security Bundle",
                    "price": "$79.99",
                    "category": "network_security",
                    "description": "Complete router and network protection"
                },
                {
                    "id": 4,
                    "name": "WiFi Encryption Tool",
                    "price": "$19.99",
                    "category": "network_security",
                    "description": "Advanced encryption for your wireless network"
                }
            ]
        },
        "malware_protection": {
            "message": "To protect against malware and viruses, I recommend:",
            "products": [
                {
                    "id": 5,
                    "name": "Anti-Malware Pro",
                    "price": "$39.99",
                    "category": "malware_protection",
                    "description": "Powerful malware and virus removal"
                },
                {
                    "id": 6,
                    "name": "Real-time Malware Shield",
                    "price": "$59.99",
                    "category": "malware_protection",
                    "description": "Continuous malware protection and quarantine"
                }
            ]
        }
    }
}

DEFAULT_RESPONSES = {
    "pl": {
        "message": "Chętnie pomogę w kwestiach cyberbezpieczeństwa! Zapytaj mnie o ochronę urządzeń, bezpieczeństwo sieci lub ochronę przed wirusami i złośliwym oprogramowaniem.",
        "products": []
    },
    "en": {
        "message": "I'm here to help with cybersecurity questions! Ask me about device protection, network security, or malware prevention.",
        "products": []
    }
}


@app.get("/")
def home():
    return {
        "message": "AI Cybersecurity Store API running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/api/recommendation")
def get_recommendation(
    request: RecommendationRequest
):
    text = request.message
    lang = (request.language or "pl").lower()[:2]
    if lang not in ["pl", "en"]:
        lang = "pl"

    prediction, probabilities, classes = predict_intent(
        text
    )

    # Get confidence score (max probability)
    confidence = float(max(probabilities))

    lang_recommendations = PRODUCT_RECOMMENDATIONS.get(lang, PRODUCT_RECOMMENDATIONS["pl"])
    lang_default = DEFAULT_RESPONSES.get(lang, DEFAULT_RESPONSES["pl"])

    # If confidence is below threshold (~0.45 for 3 classes), fallback to default guidance
    if confidence < 0.45:
        recommendation_data = lang_default
        intent = "general_query"
    else:
        recommendation_data = lang_recommendations.get(
            prediction,
            lang_default
        )
        intent = prediction

    return {
        "intent": intent,
        "confidence": confidence,
        "language": lang,
        "message": recommendation_data["message"],
        "products": recommendation_data["products"]
    }


# Keep old endpoint for backwards compatibility
@app.post("/recommendation")
def get_recommendation_legacy(
    request: RecommendationRequest
):
    text = request.message

    prediction, probabilities, classes = predict_intent(
        text
    )

    return {
        "prediction": prediction,
        "probabilities": probabilities.tolist(),
        "classes": classes.tolist()
    }