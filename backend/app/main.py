from fastapi import FastAPI

app = FastAPI(
    title="TraceRoot API",
    description="Agentic AI Incident Investigation Platform",
    version="0.1.0"
)

@app.get("/health")
def health_check():
    return{
        "status": "healthy",
        "service": "traceroot-api",
    }