from app.orchestration.investigation_graph import (
    build_investigation_graph,
)

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

    print("\n===================================")
    print("TraceRoot Day 5 Investigation")
    print("===================================\n")

    result = graph.invoke(initial_state)

    print("Investigation Summary")
    print("-----------------------------------")
    print(f"Iterations: {result['iteration']}")
    print(f"Current step: {result['current_step']}")
    print(f"Evidence count: {len(result['evidence'])}")
    print(
        f"Executed actions: "
        f"{len(result['executed_actions'])}"
    )

    print("\nExecuted Actions")
    print("-----------------------------------")

    for action in result["executed_actions"]:
        print(f"- {action}")

    print("\nEvidence Collected")
    print("-----------------------------------")

    for index, evidence in enumerate(
        result["evidence"],
        start=1,
    ):
        print(f"\nEvidence #{index}")
        print(f"Source: {evidence.source_type}")
        print(f"Service: {evidence.service}")
        print(f"Content: {evidence.content}")
        print(
            f"Relevance: "
            f"{evidence.relevance_score}"
        )

    print("\nCurrent Hypothesis")
    print("-----------------------------------")

    if result["hypotheses"]:
        hypothesis = result["hypotheses"][0]

        print(f"Description: {hypothesis.description}")
        print(f"Confidence: {hypothesis.confidence}")
        print(f"Status: {hypothesis.status}")

        print("\nSupporting Evidence:")

        for item in hypothesis.supporting_evidence:
            print(f"- {item}")

        print("\nContradicting Evidence:")

        if hypothesis.contradicting_evidence:
            for item in hypothesis.contradicting_evidence:
                print(f"- {item}")
        else:
            print("- None")
    else:
        print("No hypothesis generated.")

    print("\n===================================")
    print("FINAL RCA REPORT")
    print("===================================\n")

    if result["final_report"]:
        print(result["final_report"])
    else:
        print("No final report generated.")

    print("\n===================================")
    print("Investigation finished")
    print("===================================\n")


if __name__ == "__main__":
    main()