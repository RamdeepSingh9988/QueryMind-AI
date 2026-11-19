from fastapi import FastAPI

app = FastAPI(
    title="QueryMind AI",
    description="Text-to-SQL with Intelligent Clarification",
    version="0.1.0"
)

@app.get("/")
def home():
    return {
        "project": "QueryMind AI",
        "message": "Welcome to QueryMind AI",
    }

@app.get("/health")
def health():
    return {"status": "ok"}