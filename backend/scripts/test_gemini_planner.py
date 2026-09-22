from app.orchestration.investigation_graph import plan_next_action
from app.schemas.incident import Incident, IncidentSeverity
from app.schemas.investigation import InvestigationState


incident = Incident(
    id="INC-001",
    title="Checkout payment failures",
    description="Payment failures increased after deployment",
    service="payment-service",
    severity=IncidentSeverity.CRITICAL,
)

state = InvestigationState(
    incident=incident,
)

result = plan_next_action(state)

decision = result["current_decision"]

print("\n--- TraceRoot Planner Decision ---")
print("Action:", decision.action)
print("Reason:", decision.reason)
print("Parameters:", decision.parameters)
print("Current step:", result["current_step"])