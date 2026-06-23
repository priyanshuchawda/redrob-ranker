from __future__ import annotations

from .evidence_ledger import build_evidence_ledger
from .job_understanding import RoleRequirementMatrix
from .models import ScoredCandidate
from .risk import build_risk_radar


def compare_scored_candidates(
    candidate_a: ScoredCandidate,
    candidate_b: ScoredCandidate,
    role_requirements: RoleRequirementMatrix | None = None,
) -> dict:
    ledger_a = build_evidence_ledger(candidate_a, rank=1)
    ledger_b = build_evidence_ledger(candidate_b, rank=2)
    component_diffs = _component_differences(candidate_a, candidate_b)
    evidence_differences = _evidence_differences(ledger_a, ledger_b)
    risks_a = build_risk_radar(candidate_a, role_requirements)
    risks_b = build_risk_radar(candidate_b, role_requirements)

    return {
        "candidate_a": _candidate_summary(candidate_a),
        "candidate_b": _candidate_summary(candidate_b),
        "why_a_ranks_above_b": _why_a_above_b(candidate_a, candidate_b, component_diffs),
        "where_b_is_stronger": _where_b_stronger(component_diffs),
        "score_component_differences": component_diffs,
        "evidence_differences": evidence_differences,
        "risks_for_a": risks_a,
        "risks_for_b": risks_b,
        "what_to_verify": _what_to_verify(ledger_a, ledger_b, risks_a, risks_b),
    }


def _candidate_summary(scored: ScoredCandidate) -> dict:
    return {
        "candidate_id": scored.candidate_id,
        "final_score": scored.product_scores.final_score,
        "fit_score": scored.product_scores.fit_score,
        "proof_score": scored.product_scores.proof_score,
        "confidence_score": scored.product_scores.confidence_score,
        "hireability_score": scored.product_scores.hireability_score,
        "risk_score": scored.product_scores.risk_score,
    }


def _component_differences(a: ScoredCandidate, b: ScoredCandidate) -> dict:
    fields = (
        "role",
        "seniority",
        "retrieval",
        "ranking",
        "evaluation",
        "skills",
        "production",
        "engineering",
        "leadership",
        "confidence",
        "availability",
        "logistics",
        "risk",
        "total",
    )
    return {
        field: round(getattr(a.components, field) - getattr(b.components, field), 4)
        for field in fields
    }


def _evidence_differences(ledger_a: dict, ledger_b: dict) -> dict:
    concepts_a = {item["concept"] for item in ledger_a.get("positive_evidence", [])}
    concepts_b = {item["concept"] for item in ledger_b.get("positive_evidence", [])}
    return {
        "a_unique_evidence": sorted(concepts_a - concepts_b)[:10],
        "b_unique_evidence": sorted(concepts_b - concepts_a)[:10],
        "shared_evidence": sorted(concepts_a & concepts_b)[:10],
        "a_missing": ledger_a.get("missing_evidence", []),
        "b_missing": ledger_b.get("missing_evidence", []),
    }


def _why_a_above_b(a: ScoredCandidate, b: ScoredCandidate, diffs: dict) -> str:
    lead = max((key for key in diffs if key != "risk"), key=lambda key: diffs[key])
    return (
        f"Candidate {a.candidate_id} ranks above Candidate {b.candidate_id} because "
        f"the total score is higher by {diffs['total']:.2f}, led by {lead}."
    )


def _where_b_stronger(diffs: dict) -> list[str]:
    stronger = [key for key, value in diffs.items() if key != "risk" and value < 0]
    return stronger or ["Candidate B is not stronger on the scored components."]


def _what_to_verify(ledger_a: dict, ledger_b: dict, risks_a: list[dict], risks_b: list[dict]) -> list[str]:
    items: list[str] = []
    for ledger, label in ((ledger_a, "Candidate A"), (ledger_b, "Candidate B")):
        missing = ledger.get("missing_evidence", [])
        if missing:
            items.append(f"{label}: verify {missing[0]}.")
    if risks_a:
        items.append(f"Candidate A: clarify {risks_a[0]['risk_type']}.")
    if risks_b:
        items.append(f"Candidate B: clarify {risks_b[0]['risk_type']}.")
    return items or ["Verify production ownership, metrics, and current availability for both candidates."]

