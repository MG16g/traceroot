class ToolError(Exception):
    """Base exception for TraceRoot tools."""


class TelemetryNotFoundError(ToolError):
    """Raised when telemetry for an incident does not exist."""


class TelemetryParseError(ToolError):
    """Raised when telemetry exists but cannot be parsed."""