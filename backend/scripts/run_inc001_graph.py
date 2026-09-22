from app.orchestration.investigation_graph import build_investigation_graph

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import InvestigationState


def main():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    initial_state = InvestigationState(
        incident=incident,
    )

    graph = build_investigation_graph()

    result = graph.invoke(initial_state)

    print("\n===================================")
    print("TraceRoot Day 4 Investigation")
    print("===================================")

    decision = result["current_decision"]

    print("\nDecision")
    print("-----------------------------------")
    print("Action:", decision.action)
    print("Reason:", decision.reason)
    print("Parameters:", decision.parameters)

    print("\nGraph State")
    print("-----------------------------------")
    print("Current step:", result["current_step"])
    print("Error:", result.get("error"))

    evidence = result["evidence"]

    print("\nEvidence Collected")
    print("-----------------------------------")
    print("Count:", len(evidence))

    for index, item in enumerate(evidence, start=1):
        print(f"\nEvidence #{index}")
        print("Source:", item.source_type)
        print("Service:", item.service)
        print("Content:", item.content)

    print("\n===================================")
    print("Investigation finished")
    print("===================================")


if __name__ == "__main__":
    main()