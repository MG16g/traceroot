from fastapi import FastAPI

from app.api.investigations import (
    router as investigations_router,
)


app = FastAPI(
    title="TraceRoot API",
    description="Agentic AI Incident Investigation Platform",
    version="0.1.0"
)

app.include_router(investigations_router)


@app.get("/health")
def health_check():
    return{
        "status": "healthy",
        "service": "traceroot-api",
    }