from app.llm.provider import get_llm

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
)


def main():
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        InvestigationDecision
    )

    prompt = """
You are an SRE investigation planner.

An incident occurred in payment-service:
checkout payment failures increased immediately
after a deployment.

Choose exactly one next investigation action.

Available actions and allowed parameters:

search_logs:
- service
- level
- query

query_metrics:
- service
- metric
- start_time
- end_time

get_deployments:
- service
- status
- start_time
- end_time

stop:
- no parameters

Do not invent parameter names.
Only use parameters listed for the selected action.

Return the most appropriate investigation decision.
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