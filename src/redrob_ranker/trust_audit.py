from __future__ import annotations

from collections import Counter
from typing import Any, Mapping


def build_trust_audit(payload: Mapping[str, Any]) -> dict[str, Any]:
    rows = list(payload.get("rankings", []) or [])
    total = int(payload.get("metadata", {}).get("candidate_count") or len(rows))
    shortlisted = len(rows)
    confidences = [_num(row.get("confidence_score")) for row in rows]
    proof_scores = [_num(row.get("proof_score")) for row in rows]
    high_risk = [row for row in rows if _num(row.get("risk_score")) >= 50 or row.get("risks")]
    missing_rows = [row for row in rows if row.get("missing_evidence")]
    weak_proof = [
        row
        for row in rows
        if any(_risk_type(risk) in {"keyword stuffing", "weak proof behind strong claims", "generic ai without shipped retrieval evidence"} for risk in row.get("risks", []))
        or any("weak proof" in str(tag).casefold() for tag in row.get("review_tags", []))
    ]
    location_availability = [
        row
        for row in rows
        if any(term in " ".join(map(str, row.get("review_tags", []))).casefold() for term in ("location", "availability"))
        or any(any(term in _risk_type(risk) for term in ("location", "availability", "relocate")) for risk in row.get("risks", []))
    ]
    low_confidence = [row for row in rows if _num(row.get("confidence_score")) < 45]

    risk_severity = Counter(str(risk.get("severity", "unknown")) for row in rows for risk in row.get("risks", []) if isinstance(risk, Mapping))
    missing_categories = Counter(str(item) for row in rows for item in row.get("missing_evidence", []))
    evidence_items = [
        item
        for row in rows
        for group in ("positive_evidence", "negative_evidence")
        for item in row.get("evidence_ledger", {}).get(group, [])
        if isinstance(item, Mapping)
    ]
    proof_vs_claim = Counter(str(item.get("claim_or_proof", "unknown")) for item in evidence_items)
    score_distribution = {
        "0-39": sum(_num(row.get("final_score")) < 40 for row in rows),
        "40-59": sum(40 <= _num(row.get("final_score")) < 60 for row in rows),
        "60-79": sum(60 <= _num(row.get("final_score")) < 80 for row in rows),
        "80-100": sum(_num(row.get("final_score")) >= 80 for row in rows),
    }

    return {
        "total_candidates": total,
        "shortlisted_candidates": shortlisted,
        "average_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0.0,
        "average_proof_score": round(sum(proof_scores) / len(proof_scores), 2) if proof_scores else 0.0,
        "high_risk_candidate_count": len(high_risk),
        "candidates_with_missing_evidence": len(missing_rows),
        "keyword_stuffing_or_weak_proof_count": len(weak_proof),
        "location_or_availability_risk_count": len(location_availability),
        "low_confidence_count": len(low_confidence),
        "proxy_evaluation_warning": _proxy_warning(payload),
        "score_distribution": score_distribution,
        "risk_severity_counts": dict(risk_severity),
        "missing_evidence_categories": dict(missing_categories.most_common(8)),
        "proof_vs_claim_summary": dict(proof_vs_claim),
    }


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _risk_type(risk: Any) -> str:
    if isinstance(risk, Mapping):
        return str(risk.get("risk_type", "")).casefold()
    return str(risk).casefold()


def _proxy_warning(payload: Mapping[str, Any]) -> str:
    metadata = payload.get("metadata", {}) if isinstance(payload.get("metadata"), Mapping) else {}
    if metadata.get("labels_supplied"):
        return ""
    return "No labels supplied for this run; evaluation and trust counts are audit/proxy signals, not recruiter accuracy."
