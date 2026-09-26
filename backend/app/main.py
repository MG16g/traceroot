from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.investigations import (
    router as investigations_router,
)


app = FastAPI(
    title="TraceRoot API",
    description="Agentic AI Incident Investigation Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(investigations_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "traceroot-api",
    }