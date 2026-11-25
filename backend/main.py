
from fastapi import FastAPI


app = FastAPI(
    title="QueryMind AI",
    description="AI-powered natural language to SQL platform",
    version="1.0.0"
)


@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "QueryMind AI",
        "version": "1.0.0"
    }
