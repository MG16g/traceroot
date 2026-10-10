import os


TRACEROOT_INGEST_URL = os.getenv(
    "TRACEROOT_INGEST_URL",
    "http://127.0.0.1:8000/api/telemetry/ingest",
)

TRACEROOT_TELEMETRY_API_KEY = os.getenv(
    "TRACEROOT_TELEMETRY_API_KEY",
)

TELEMETRY_ENABLED = (
    os.getenv("TELEMETRY_ENABLED", "false").lower()
    == "true"
)