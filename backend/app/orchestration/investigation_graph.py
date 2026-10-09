from uuid import uuid4

from langgraph.graph import StateGraph, START, END

import logging

logger = logging.getLogger(__name__)

from app.llm.provider import get_llm

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
    InvestigationStatus,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisProposal,
    HypothesisStatus,
)

from app.tools.telemetry_catalog import (
    get_telemetry_catalog,
    format_telemetry_catalog,
)

from app.tools.log_tool import search_logs
from app.tools.metric_tool import query_metrics
from app.tools.deployment_tool import get_deployments
from app.services.rca_evaluator import evaluate_hypothesis
from app.schemas.root_cause import RootCauseStatus


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
        "evaluate_root_cause",
        evaluate_root_cause,
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

    builder.add_conditional_edges(
        "execute_action",
        route_after_action,
        {
            "plan_next_action": "plan_next_action",
            "update_hypothesis": "update_hypothesis",
        },
    )

    # Hypothesis -> continue investigation OR report
    builder.add_edge(
        "update_hypothesis",
        "evaluate_root_cause",
    )

    builder.add_conditional_edges(
        "evaluate_root_cause",
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

    telemetry_catalog = get_telemetry_catalog(
    state.incident.id
    )

    telemetry_context = format_telemetry_catalog(
        telemetry_catalog
    )


    notes_context = format_investigation_notes(
        state.investigation_notes
    )

    executed_actions_context = format_executed_actions(
        state.executed_actions
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

Telemetry available for this incident:
{telemetry_context}

Previous investigation notes:
{notes_context}

If a previous action returned no results, do not repeat
the same action with identical parameters.

Use the empty result as investigation feedback.

Consider broadening the query, removing an unnecessary
filter, or investigating another telemetry source.

Investigation strategy:

- Use the telemetry catalog when selecting parameter values.
- Do not invent service names, metric names, log levels,
  or deployment statuses.
- Prefer evidence sources that have not yet been investigated.
- If an action returned no results, do not repeat the exact
  same action and parameters.
- Treat an empty result as useful investigation feedback.
- When a filtered query returns no results, consider removing
  an optional filter or using a broader valid query.
- Do not repeatedly change arbitrary filters on the same tool
  when another telemetry source remains unexplored.
- Prefer gathering evidence from multiple source types:
  deployments, logs, and metrics.
- Stop only when further investigation is unnecessary.


Investigation actions already executed:
{executed_actions_context}

IMPORTANT:
Do not select an action with the same parameters as any
action listed above.

After collecting useful evidence from one telemetry source,
prefer investigating a different telemetry source.

For example, if logs already provide evidence, consider
metrics or deployments next.

Try to gather evidence from multiple independent telemetry
source types before stopping.

Return only a JSON object matching this structure:

{{
  "action": "search_logs | query_metrics | get_deployments | stop",
  "reason": "brief explanation",
  "parameters": {{}}
}}

Do not include markdown.
Do not include code fences.
Do not include commentary outside the JSON object.

Do not include optional parameters with empty string values.
Omit an optional parameter when it is not needed.

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
Only use parameters listed for the selected action. 
"""

    llm = get_llm()

    # IMPORTANT:
    # structured output FIRST, retry SECOND
    structured_llm = llm.with_structured_output(
        InvestigationDecision,
        method="json_mode",
    )

    retrying_llm = with_llm_retry(
        structured_llm,
    )

    decision = retrying_llm.invoke(
        prompt
    )

    # Prevent the investigation from stopping before
    # attempting any telemetry collection.
    if (
        decision.action == InvestigationAction.STOP
        and not state.executed_actions
    ):
        decision = InvestigationDecision(
            action=InvestigationAction.SEARCH_LOGS,
            reason=(
                "Collect initial log evidence before "
                "allowing investigation termination."
            ),
            parameters={},
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

    fingerprint = build_action_fingerprint(decision)

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
        action_fingerprint = build_action_fingerprint(
            decision
        )

        logger.exception(
            "TraceRoot telemetry action failed: "
            "incident=%s action=%s parameters=%s",
            incident_id,
            decision.action.value,
            parameters,
        )

        return {
            "current_step": "tool_error",
            "error": str(exc),
            "executed_actions": (
                state.executed_actions
                + [action_fingerprint]
            ),
            "investigation_notes": (
                state.investigation_notes
                + [
                    f"Telemetry action failed: "
                    f"{action_fingerprint}: {exc}"
                ]
            ),
        }

    new_evidence = tool_results_to_evidence(
        incident_id=incident_id,
        action=decision.action,
        results=results,
    )

    action_fingerprint = build_action_fingerprint(
        decision
    )

    if not results:
        action_fingerprint = build_action_fingerprint(
            decision
        )

        note = (
            f"Investigation action returned no results: "
            f"{action_fingerprint}"
        )

        return {
            "evidence": state.evidence,
            "executed_actions": (
                state.executed_actions
                + [action_fingerprint]
            ),
            "investigation_notes": (
                state.investigation_notes
                + [note]
            ),
            "current_step": "no_results",
            "error": None,
        }

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

Before selecting evidence references, critically evaluate
the proposed hypothesis against every available evidence record.

Identify observations that:
- Directly conflict with the proposed explanation.
- Suggest a competing root cause.
- Show the suspected component was healthy during the failure.
- Weaken the proposed causal relationship.

Do not classify evidence as supporting merely because it
mentions the affected service or occurred near the incident.

Only include genuine contradictions supported by the supplied
evidence. Never fabricate or invent contradictory evidence.

If no supplied evidence contradicts the hypothesis, return
an empty contradicting_evidence list.

Confidence must be between 0 and 1.

Do not generate IDs or incident metadata.
Return only a valid JSON object matching this exact structure:

{{
    "description": "A concise evidence-backed hypothesis",
    "supporting_evidence": [
        "Evidence #1",
        "Evidence #2"
    ],
    "contradicting_evidence": [
        "Evidence #3"
    ],
    "confidence": 0.75
}}

IMPORTANT JSON requirements:

- supporting_evidence must be a JSON array of strings.
- contradicting_evidence must be a JSON array of strings.
- Every evidence reference must use the exact string format
  "Evidence #N".
- Never return evidence references as integers.
- Correct: ["Evidence #1", "Evidence #2"]
- Incorrect: [1, 2]
- Only reference evidence actually supplied above.
- If there is no supporting evidence, return [].
- If there is no contradicting evidence, return [].
- confidence must be a number between 0.0 and 1.0.
- Do not include markdown.
- Do not include code fences.
- Do not include commentary outside the JSON object.

Do not infer facts that are not present in the supplied evidence.

A statement from the incident description is context, not automatically
confirmed evidence.

For example, if the incident description says failures increased after
a deployment but no deployment evidence has been collected yet, you may
describe the deployment as a possible factor, but you must not state
that the deployment caused the failure.

Base supporting_evidence only on the evidence records supplied above.

Distinguish correlation from causation.
"""

    llm = get_llm()

    # Structured output FIRST
    structured_llm = llm.with_structured_output(
        HypothesisProposal,
        method="json_mode",
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
    candidate = state.root_cause_candidate

    if candidate is None:
        return False

    # Require enough total telemetry before allowing
    # the autonomous investigation to terminate.
    if len(state.evidence) < 3:
        return False

    # Require evidence from at least two independent
    # telemetry source types.
    if len(candidate.source_types) < 2:
        return False

    # Confidence is now calculated by TraceRoot's
    # deterministic RCA evaluator.
    if candidate.confidence < 0.70:
        return False

    if candidate.status != RootCauseStatus.SUPPORTED:
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

    root_cause_context = format_root_cause_for_report(
        state
    )

    llm = get_llm()

    prompt = f"""
You are the final RCA report writer for TraceRoot.

Generate a concise Site Reliability Engineering incident
investigation report using only the supplied incident,
evidence, hypotheses, and deterministic root cause evaluation.

Do not invent evidence.

Do not increase or override the deterministic confidence score.

The deterministic root cause evaluation is authoritative
for RCA confidence and RCA status.

Incident:
{state.incident.model_dump_json(indent=2)}

Evidence:
{evidence_context}

LLM-generated investigation hypotheses:
{hypothesis_context}

TraceRoot deterministic root cause evaluation:
{root_cause_context}

Write the report with these sections:

# Incident Summary

# Investigation Findings

# Root Cause Hypothesis

# Supporting Evidence

# Contradicting Evidence

# Confidence

# Recommended Next Steps

Rules:

- Clearly distinguish confirmed observations from hypotheses.
- Use the deterministic root cause confidence in the
  Confidence section when a root cause candidate exists.
- Do not substitute the LLM hypothesis confidence for the
  deterministic confidence.
- State when the root cause remains under investigation.
- Do not claim causation beyond the available evidence.
"""

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        report = response.content
    else:
        report = str(response)

    return {
        "final_report": report,
        "current_step": "completed",
        "status": InvestigationStatus.COMPLETED,
    }

def route_after_action(
    state: InvestigationState,
) -> str:
    if state.current_step in {
        "no_results",
        "tool_error",
    }:
        return "plan_next_action"

    if state.current_step == "evidence_collected":
        return "update_hypothesis"

    raise ValueError(
        "Unexpected investigation step after tool execution: "
        f"{state.current_step}"
    )


def format_investigation_notes(
    notes: list[str],
) -> str:
    if not notes:
        return "No investigation notes yet."

    return "\n".join(
        f"- {note}"
        for note in notes
    )


def format_executed_actions(
    actions: list[str],
) -> str:
    if not actions:
        return "No investigation actions have been executed yet."

    return "\n".join(
        f"- {action}"
        for action in actions
    )


def evaluate_root_cause(
    state: InvestigationState,
):
    if not state.hypotheses:
        return {
            "root_cause_candidate": None,
            "current_step": "no_root_cause_candidate",
        }

    hypothesis = state.hypotheses[0]

    candidate = evaluate_hypothesis(
        hypothesis=hypothesis,
        evidence_items=state.evidence,
    )

    return {
        "root_cause_candidate": candidate,
        "current_step": "root_cause_evaluated",
    }

def format_root_cause_for_report(
    state: InvestigationState,
) -> str:
    candidate = state.root_cause_candidate

    if candidate is None:
        return (
            "No deterministic root cause candidate "
            "was established."
        )

    return f"""
Root Cause Description:
{candidate.description}

Deterministic Confidence:
{candidate.confidence:.2f}

Evaluation Status:
{candidate.status.value}

Supporting Evidence References:
{candidate.supporting_evidence}

Contradicting Evidence References:
{candidate.contradicting_evidence}

Supporting Source Types:
{candidate.source_types}
""".strip()