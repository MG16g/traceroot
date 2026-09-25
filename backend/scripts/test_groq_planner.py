from app.llm.provider import get_llm

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
)


def main():
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        InvestigationDecision,
        method="json_mode",
    )

    prompt = """
You are the investigation planner for TraceRoot.

Incident:
Checkout payment failures increased after a deployment.

Service:
payment-service

Available investigation actions:
- search_logs
- query_metrics
- get_deployments
- stop

Choose the single most appropriate next investigation action.

Return ONLY a valid JSON object with this structure:

{
    "action": "search_logs",
    "reason": "brief explanation",
    "parameters": {
        "service": "payment-service"
    }
}

The action must be one of:
- search_logs
- query_metrics
- get_deployments
- stop

Do not include markdown.
Do not include code fences.
Do not include text outside the JSON object.
"""

    decision = structured_llm.invoke(prompt)

    print("\n===================================")
    print("TraceRoot Groq Structured Test")
    print("===================================")

    print(f"Type: {type(decision)}")
    print(f"Action: {decision.action}")
    print(f"Reason: {decision.reason}")
    print(f"Parameters: {decision.parameters}")

    print("\nValidation")
    print("-----------------------------------")

    assert isinstance(
        decision,
        InvestigationDecision,
    )

    assert isinstance(
        decision.action,
        InvestigationAction,
    )

    print("Structured output validation: PASSED")


if __name__ == "__main__":
    main()