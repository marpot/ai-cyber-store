from fastapi import FastAPI
from pydantic import BaseModel

from nlp.predict import predict_intent


app = FastAPI(
    title="AI Cybersecurity Store API",
    version="1.0.0"
)


class RecommendationRequest(BaseModel):
    message: str


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


@app.post("/recommendation")
def get_recommendation(
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