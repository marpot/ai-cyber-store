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


# Product recommendations mapping based on detected intent
PRODUCT_RECOMMENDATIONS = {
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

DEFAULT_RESPONSE = {
    "message": "I'm here to help with cybersecurity questions! Ask me about device protection, network security, or malware prevention.",
    "products": []
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

    prediction, probabilities, classes = predict_intent(
        text
    )

    # Get confidence score (max probability)
    confidence = max(probabilities)

    # Get recommendation based on predicted intent
    recommendation_data = PRODUCT_RECOMMENDATIONS.get(
        prediction,
        DEFAULT_RESPONSE
    )

    return {
        "intent": prediction,
        "confidence": float(confidence),
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