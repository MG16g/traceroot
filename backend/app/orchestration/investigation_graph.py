from uuid import uuid4

from langgraph.graph import StateGraph, START, END

from app.llm.provider import get_llm

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisProposal,
    HypothesisStatus,
)

from app.tools.log_tool import search_logs
from app.tools.metric_tool import query_metrics
from app.tools.deployment_tool import get_deployments


MAX_ITERATIONS = 5


# ============================================================
# LLM RETRY
# ============================================================

def with_llm_retry(runnable):
    """
    Add retry behavior to real LangChain runnables.

    Simple fake LLMs used in unit tests may not implement
    with_retry(), so return them unchanged.
    """
    if not hasattr(runnable, "with_retry"):
        return runnable

    return runnable.with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True,
    )


# ============================================================
# GRAPH
# ============================================================

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

    builder.add_node(
        "update_hypothesis",
        update_hypotheses,
    )

    builder.add_node(
        "handle_duplicate_action",
        handle_duplicate_action,
    )

    builder.add_node(
        "generate_final_report",
        generate_final_report,
    )

    # START -> planner
    builder.add_edge(
        START,
        "plan_next_action",
    )

    # Planner routing
    builder.add_conditional_edges(
        "plan_next_action",
        route_action,
        {
            "stop": "generate_final_report",
            "execute_action": "execute_action",
            "duplicate": "handle_duplicate_action",
        },
    )

    # Tool -> hypothesis analysis
    builder.add_edge(
        "execute_action",
        "update_hypothesis",
    )

    # Hypothesis -> continue investigation OR report
    builder.add_conditional_edges(
        "update_hypothesis",
        route_after_hypothesis,
        {
            "continue": "plan_next_action",
            "stop": "generate_final_report",
        },
    )

    # Duplicate action -> planner reconsideration
    builder.add_edge(
        "handle_duplicate_action",
        "plan_next_action",
    )

    # Report -> END
    builder.add_edge(
        "generate_final_report",
        END,
    )

    return builder.compile()


# ============================================================
# PLANNER
# ============================================================

def plan_next_action(
    state: InvestigationState,
):
    evidence_context = format_evidence_for_planner(
        state.evidence
    )

    hypothesis_context = format_hypotheses_for_planner(
        state.hypotheses
    )

    prompt = f"""
You are the investigation planner for TraceRoot.

Your responsibility is to choose the next investigation capability.
Do not determine the final root cause.

Incident:
{state.incident.model_dump_json(indent=2)}

Current investigation step:
{state.current_step}

Current investigation iteration:
{state.iteration}

Evidence collected so far:
{evidence_context}

Current hypotheses:
{hypothesis_context}

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

Choose the single most appropriate next action.

Prefer actions that help test, strengthen, or challenge
the current hypothesis.

Avoid repeating an investigation that has already
been performed.

Do not invent parameter names.
Only use parameters listed for the selected action. """

    llm = get_llm()

    # IMPORTANT:
    # structured output FIRST, retry SECOND
    structured_llm = llm.with_structured_output(
        InvestigationDecision
    )

    retrying_llm = with_llm_retry(
        structured_llm
    )

    decision = retrying_llm.invoke(
        prompt
    )

    return {
        "current_decision": decision,
        "current_step": "action_selected",
        "iteration": state.iteration + 1,
    }


# ============================================================
# PLANNER ROUTING
# ============================================================

def route_action(
    state: InvestigationState,
) -> str:
    decision = state.current_decision

    if decision is None:
        raise ValueError(
            "Cannot route investigation without a current decision."
        )

    if decision.action == InvestigationAction.STOP:
        return "stop"

    if state.iteration >= MAX_ITERATIONS:
        return "stop"

    fingerprint = build_action_fingerprint(
        decision
    )

    if fingerprint in state.executed_actions:
        return "duplicate"

    return "execute_action"


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_action(
    state: InvestigationState,
):
    decision = state.current_decision

    if decision is None:
        raise ValueError(
            "Cannot execute investigation action without a current decision."
        )

    incident_id = state.incident.id
    parameters = decision.parameters

    try:
        if (
            decision.action
            == InvestigationAction.SEARCH_LOGS
        ):
            results = search_logs(
                incident_id=incident_id,
                **parameters,
            )

        elif (
            decision.action
            == InvestigationAction.QUERY_METRICS
        ):
            results = query_metrics(
                incident_id=incident_id,
                **parameters,
            )

        elif (
            decision.action
            == InvestigationAction.GET_DEPLOYMENTS
        ):
            results = get_deployments(
                incident_id=incident_id,
                **parameters,
            )

        else:
            raise ValueError(
                f"Unsupported executable action: "
                f"{decision.action}"
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

    action_fingerprint = build_action_fingerprint(
        decision
    )

    return {
        "evidence": (
            state.evidence
            + new_evidence
        ),
        "executed_actions": (
            state.executed_actions
            + [action_fingerprint]
        ),
        "current_step": "evidence_collected",
        "error": None,
    }


# ============================================================
# TOOL RESULTS -> EVIDENCE
# ============================================================

def tool_results_to_evidence(
    incident_id: str,
    action: InvestigationAction,
    results: list[dict],
) -> list[Evidence]:

    source_type_map = {
        InvestigationAction.SEARCH_LOGS:
            EvidenceSourceType.LOG,

        InvestigationAction.QUERY_METRICS:
            EvidenceSourceType.METRIC,

        InvestigationAction.GET_DEPLOYMENTS:
            EvidenceSourceType.DEPLOYMENT,
    }

    source_type = source_type_map[action]

    evidence_items = []

    for result in results:
        evidence = Evidence(
            id=str(uuid4()),
            incident_id=incident_id,
            source_type=source_type,
            service=result.get(
                "service",
                "unknown",
            ),
            content=str(result),
            relevance_score=1.0,
        )

        evidence_items.append(
            evidence
        )

    return evidence_items


# ============================================================
# EVIDENCE FORMATTING
# ============================================================

def format_evidence_for_planner(
    evidence_items: list[Evidence],
) -> str:

    if not evidence_items:
        return (
            "No evidence has been collected yet."
        )

    lines = []

    for index, evidence in enumerate(
        evidence_items,
        start=1,
    ):
        lines.append(
            f"""
Evidence #{index}
Source: {evidence.source_type.value}
Service: {evidence.service}
Content: {evidence.content}
"""
        )

    return "\n".join(lines)


# ============================================================
# ACTION FINGERPRINT
# ============================================================

def build_action_fingerprint(
    decision: InvestigationDecision,
) -> str:

    parameters = ",".join(
        f"{key}={value}"
        for key, value in sorted(
            decision.parameters.items()
        )
    )

    return (
        f"{decision.action.value}"
        f"|{parameters}"
    )


# ============================================================
# DUPLICATE ACTION
# ============================================================

def handle_duplicate_action(
    state: InvestigationState,
):
    return {
        "current_step":
            "duplicate_action_skipped",
    }


# ============================================================
# HYPOTHESIS GENERATION
# ============================================================

def update_hypotheses(
    state: InvestigationState,
):
    if not state.evidence:
        return {
            "hypotheses":
                state.hypotheses,

            "current_step":
                "no_hypothesis_evidence",
        }

    evidence_context = format_evidence_for_planner(
        state.evidence
    )

    prompt = f"""
You are the hypothesis analysis component of TraceRoot.

Your job is to form one evidence-backed hypothesis about
the production incident.

Do not claim causation unless the available evidence supports it.

Incident:
{state.incident.model_dump_json(indent=2)}

Evidence:
{evidence_context}

Create one current hypothesis.

Supporting evidence should reference evidence that supports
the hypothesis.

Contradicting evidence should contain evidence that weakens
or challenges the hypothesis.

Confidence must be between 0 and 1.

Do not generate IDs or incident metadata.
"""

    llm = get_llm()

    # Structured output FIRST
    structured_llm = llm.with_structured_output(
        HypothesisProposal
    )

    # Retry wrapper SECOND
    retrying_llm = with_llm_retry(
        structured_llm
    )

    proposal = retrying_llm.invoke(
        prompt
    )

    hypothesis = Hypothesis(
        id=str(uuid4()),
        incident_id=state.incident.id,
        description=proposal.description,
        supporting_evidence=(
            proposal.supporting_evidence
        ),
        contradicting_evidence=(
            proposal.contradicting_evidence
        ),
        confidence=proposal.confidence,
        status=(
            HypothesisStatus.INVESTIGATING
        ),
    )

    return {
        "hypotheses": [
            hypothesis
        ],
        "current_step":
            "hypothesis_updated",
    }


# ============================================================
# HYPOTHESIS FORMATTING
# ============================================================

def format_hypotheses_for_planner(
    hypotheses: list[Hypothesis],
) -> str:

    if not hypotheses:
        return (
            "No hypothesis has been formed yet."
        )

    lines = []

    for index, hypothesis in enumerate(
        hypotheses,
        start=1,
    ):
        lines.append(
            f"""
Hypothesis #{index}
Description: {hypothesis.description}
Confidence: {hypothesis.confidence}
Status: {hypothesis.status.value}

Supporting evidence:
{hypothesis.supporting_evidence}

Contradicting evidence:
{hypothesis.contradicting_evidence}
"""
        )

    return "\n".join(lines)


# ============================================================
# INVESTIGATION SUFFICIENCY
# ============================================================

def has_sufficient_evidence(
    state: InvestigationState,
) -> bool:

    # Need a hypothesis first
    if not state.hypotheses:
        return False

    # Need at least three evidence items
    if len(state.evidence) < 3:
        return False

    # Need multiple evidence source types
    source_types = {
        evidence.source_type
        for evidence in state.evidence
    }

    if len(source_types) < 2:
        return False

    current_hypothesis = (
        state.hypotheses[0]
    )

    # Confidence threshold
    if (
        current_hypothesis.confidence
        < 0.70
    ):
        return False

    return True


# ============================================================
# POST-HYPOTHESIS ROUTING
# ============================================================

def route_after_hypothesis(
    state: InvestigationState,
) -> str:

    if has_sufficient_evidence(
        state
    ):
        return "stop"

    return "continue"


# ============================================================
# FINAL RCA REPORT
# ============================================================

def generate_final_report(
    state: InvestigationState,
):
    evidence_context = format_evidence_for_planner(
        state.evidence
    )

    hypothesis_context = format_hypotheses_for_planner(
        state.hypotheses
    )

    prompt = f"""
You are the final RCA report writer for TraceRoot.

Generate a concise Site Reliability Engineering incident
investigation report using only the supplied incident,
evidence, and hypotheses.

Do not invent evidence or claim certainty that is not
supported by the investigation.

Incident:
{state.incident.model_dump_json(indent=2)}

Evidence:
{evidence_context}

Current hypotheses:
{hypothesis_context}

Write the report with these sections:

# Incident Summary

# Investigation Findings

# Root Cause Hypothesis

# Supporting Evidence

# Contradicting Evidence

# Confidence

# Recommended Next Steps

Clearly distinguish between confirmed facts and hypotheses.
"""

    llm = get_llm()

    retrying_llm = with_llm_retry(
        llm
    )

    response = retrying_llm.invoke(
        prompt
    )

    if hasattr(
        response,
        "content",
    ):
        report = response.content
    else:
        report = str(response)

    return {
        "final_report": report,
        "current_step": "completed",
    }