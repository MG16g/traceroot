from uuid import uuid4

from app.schemas.evidence import Evidence, EvidenceSourceType

from app.llm.provider import get_llm

from app.schemas.investigation import (
    InvestigationDecision,
    InvestigationState,
    InvestigationAction,
)

from langgraph.graph import StateGraph, START, END

from app.schemas.investigation import InvestigationState

from app.tools.log_tool import search_logs
from app.tools.metric_tool import query_metrics
from app.tools.deployment_tool import get_deployments


def prepare_investigation(state: InvestigationState):
    return {
        "current_step": "planning",
        "iteration": state.iteration + 1,
    }


def build_investigation_graph():
    builder = StateGraph(InvestigationState)

    # Nodes
    builder.add_node(
        "plan_next_action",
        plan_next_action,
    )

    builder.add_node(
        "execute_action",
        execute_action,
    )

    # Entry point
    builder.add_edge(
        START,
        "plan_next_action",
    )

    # Conditional routing after planning
    builder.add_conditional_edges(
        "plan_next_action",
        route_action,
        {
            "stop": END,
            "execute_action": "execute_action",
        },
    )

    # Day 4 stops after one tool execution
    builder.add_edge(
        "execute_action",
        END,
    )

    return builder.compile()


def plan_next_action(state: InvestigationState):
    llm = get_llm()

    structured_llm = llm.with_structured_output(
        InvestigationDecision
    )

    prompt = f"""
You are the investigation planner for TraceRoot.

Your responsibility is to choose the next investigation capability.
Do not determine the final root cause.

Incident:
{state.incident.model_dump_json(indent=2)}

Current investigation step:
{state.current_step}

Evidence collected:
{len(state.evidence)}

Available actions:

- search_logs
- query_metrics
- get_deployments
- stop

Choose the single most appropriate next action.

Only use capabilities that TraceRoot actually provides.

For tool parameters, use only parameters appropriate for the selected
investigation tool.
"""

    decision = structured_llm.invoke(prompt)

    return {
        "current_decision": decision,
        "current_step": "action_selected",
    }


def route_action(state: InvestigationState) -> str:
    decision = state.current_decision

    if decision is None:
        raise ValueError(
            "Cannot route investigation without a current decision."
        )

    if decision.action == InvestigationAction.STOP:
        return "stop"

    return "execute_action"


def execute_action(state: InvestigationState):
    decision = state.current_decision

    if decision is None:
        raise ValueError(
            "Cannot execute investigation action without a current decision."
        )

    incident_id = state.incident.id
    parameters = decision.parameters

    try:
        if decision.action == InvestigationAction.SEARCH_LOGS:
            results = search_logs(
                incident_id=incident_id,
                **parameters,
            )

        elif decision.action == InvestigationAction.QUERY_METRICS:
            results = query_metrics(
                incident_id=incident_id,
                **parameters,
            )

        elif decision.action == InvestigationAction.GET_DEPLOYMENTS:
            results = get_deployments(
                incident_id=incident_id,
                **parameters,
            )

        else:
            raise ValueError(
                f"Unsupported executable action: {decision.action}"
            )

    except Exception as exc:
        return {
            "current_step": "tool_error",
            "error": str(exc),
        }

    new_evidence = tool_results_to_evidence(
    incident_id=incident_id,
    action=decision.action,
    results=results,
    )

    return {
        "evidence": state.evidence + new_evidence,
        "current_step": "evidence_collected",
        "error":None,
    }



def tool_results_to_evidence(
    incident_id: str,
    action: InvestigationAction,
    results: list[dict],
) -> list[Evidence]:

    source_type_map = {
        InvestigationAction.SEARCH_LOGS: EvidenceSourceType.LOG,
        InvestigationAction.QUERY_METRICS: EvidenceSourceType.METRIC,
        InvestigationAction.GET_DEPLOYMENTS: EvidenceSourceType.DEPLOYMENT,
    }

    source_type = source_type_map[action]

    evidence_items = []

    for result in results:
        evidence = Evidence(
            id=str(uuid4()),
            incident_id=incident_id,
            source_type=source_type,
            service=result.get("service", "unknown"),
            content=str(result),
            relevance_score=1.0,
        )

        evidence_items.append(evidence)

    return evidence_items