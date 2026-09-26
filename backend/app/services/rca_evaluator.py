import re

from app.schemas.evidence import Evidence

from app.schemas.hypothesis import Hypothesis
from app.schemas.root_cause import (
    RootCauseCandidate,
    RootCauseStatus,
)


EVIDENCE_REFERENCE_PATTERN = re.compile(
    r"^Evidence #(\d+)$"
)


def resolve_evidence_reference(
    reference: str,
    evidence_items: list[Evidence],
) -> Evidence | None:
    """
    Resolve an LLM evidence reference such as
    'Evidence #3' to the corresponding Evidence object.
    """

    match = EVIDENCE_REFERENCE_PATTERN.fullmatch(
        reference.strip()
    )

    if match is None:
        return None

    evidence_number = int(
        match.group(1)
    )

    # References are 1-based.
    index = evidence_number - 1

    if index < 0:
        return None

    if index >= len(evidence_items):
        return None

    return evidence_items[index]


def validate_evidence_references(
    references: list[str],
    evidence_items: list[Evidence],
) -> tuple[list[str], list[str]]:
    """
    Split evidence references into valid and invalid groups.
    """

    valid = []
    invalid = []

    for reference in references:
        evidence = resolve_evidence_reference(
            reference,
            evidence_items,
        )

        if evidence is None:
            invalid.append(reference)
        else:
            valid.append(reference)

    return valid, invalid


def calculate_confidence(
    supporting_evidence: list[Evidence],
    contradicting_evidence: list[Evidence],
) -> float:
    """
    Calculate deterministic RCA confidence from validated evidence.

    Scoring:
    - Supporting evidence count: up to 0.40
    - Source diversity: up to 0.30
    - Average relevance: up to 0.20
    - Contradiction penalty: up to -0.30

    Maximum score: 0.90
    """

    if not supporting_evidence:
        return 0.0

    # 1. Supporting evidence strength — max 0.40
    support_score = min(
        len(supporting_evidence) * 0.10,
        0.40,
    )

    # 2. Independent telemetry diversity — max 0.30
    source_types = {
        evidence.source_type
        for evidence in supporting_evidence
    }

    diversity_score = min(
        len(source_types) * 0.15,
        0.30,
    )

    # 3. Evidence relevance — max 0.20
    average_relevance = (
        sum(
            evidence.relevance_score
            for evidence in supporting_evidence
        )
        / len(supporting_evidence)
    )

    relevance_score = average_relevance * 0.20

    # 4. Contradicting evidence penalty — max 0.30
    contradiction_penalty = min(
        len(contradicting_evidence) * 0.10,
        0.30,
    )

    confidence = (
        support_score
        + diversity_score
        + relevance_score
        - contradiction_penalty
    )

    return round(
        max(0.0, min(confidence, 1.0)),
        2,
    )


def evaluate_hypothesis(
    hypothesis: Hypothesis,
    evidence_items: list[Evidence],
) -> RootCauseCandidate:
    """
    Evaluate a hypothesis against collected evidence and
    produce a deterministic root-cause candidate.
    """

    valid_supporting, _ = validate_evidence_references(
        hypothesis.supporting_evidence,
        evidence_items,
    )

    valid_contradicting, _ = validate_evidence_references(
        hypothesis.contradicting_evidence,
        evidence_items,
    )

    supporting_objects = [
        resolve_evidence_reference(
            reference,
            evidence_items,
        )
        for reference in valid_supporting
    ]

    contradicting_objects = [
        resolve_evidence_reference(
            reference,
            evidence_items,
        )
        for reference in valid_contradicting
    ]

    # References were already validated, but this keeps
    # the type/runtime contract defensive.
    supporting_objects = [
        evidence
        for evidence in supporting_objects
        if evidence is not None
    ]

    contradicting_objects = [
        evidence
        for evidence in contradicting_objects
        if evidence is not None
    ]

    confidence = calculate_confidence(
        supporting_evidence=supporting_objects,
        contradicting_evidence=contradicting_objects,
    )

    source_types = sorted({
        evidence.source_type.value
        for evidence in supporting_objects
    })

    if confidence >= 0.70:
        status = RootCauseStatus.SUPPORTED

    elif (
        contradicting_objects
        and len(contradicting_objects)
        >= len(supporting_objects)
    ):
        status = RootCauseStatus.REJECTED

    else:
        status = RootCauseStatus.INVESTIGATING

    return RootCauseCandidate(
        hypothesis_id=hypothesis.id,
        incident_id=hypothesis.incident_id,
        description=hypothesis.description,
        supporting_evidence=valid_supporting,
        contradicting_evidence=valid_contradicting,
        source_types=source_types,
        confidence=confidence,
        status=status,
    )