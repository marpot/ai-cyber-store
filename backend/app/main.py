from fastapi import FastAPI


app = FastAPI(
    title="AI Cybersecurity Store API",
    version="1.0.0"
)


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
