from datetime import datetime, timezone
import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TelemetryIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: str = Field(
        min_length=1,
        max_length=100,
    )

    event_type: Literal[
        "log",
        "metric",
        "deployment",
    ]

    timestamp: datetime

    payload: dict[str, Any]

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "Telemetry timestamp must include timezone information"
            )

        return value.astimezone(timezone.utc)


    @model_validator(mode="after")
    def validate_payload(self):
        required_fields = {
            "log": ("level", "message"),
            "metric": ("metric", "value"),
            "deployment": (
                "deployment_id",
                "version",
                "status",
            ),
        }

        for field in required_fields[self.event_type]:
            if field not in self.payload:
                raise ValueError(
                    f"{self.event_type} payload requires '{field}'"
                )

        if self.event_type == "log":
            if not isinstance(self.payload["level"], str):
                raise ValueError("Log level must be a string")

            if not isinstance(self.payload["message"], str):
                raise ValueError("Log message must be a string")

        elif self.event_type == "metric":
            if not isinstance(self.payload["metric"], str):
                raise ValueError("Metric name must be a string")

            value = self.payload["value"]

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(
                    "Metric value must be a finite number"
                )

        elif self.event_type == "deployment":
            for field in (
                "deployment_id",
                "version",
                "status",
            ):
                if not isinstance(self.payload[field], str):
                    raise ValueError(
                        f"Deployment {field} must be a string"
                    )

        return self


class TelemetryIngestResponse(BaseModel):
    event_id: str
    status: Literal["accepted"] = "accepted"