from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"


def ai_metadata(*, enabled: bool = False, model: str = DEFAULT_GEMINI_MODEL, fallback_used: bool = True) -> dict[str, Any]:
    return {
        "gemini_enabled": enabled,
        "model_used": model,
        "fallback_used": fallback_used,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def fallback_ai_jd_insight(role_requirements: dict[str, Any] | None, *, model: str = DEFAULT_GEMINI_MODEL) -> dict[str, Any]:
    matrix = role_requirements or {}
    return {
        **ai_metadata(enabled=False, model=model, fallback_used=True),
        "role_archetype": matrix.get("role_title") or "Unclear from supplied JD",
        "must_have_skills": list(matrix.get("must_have_skills") or []),
        "semantic_skill_synonyms": [],
        "strong_success_signals": list(matrix.get("strong_signal_skills") or []),
        "seniority_expectations": _listify(matrix.get("seniority_expectations")),
        "domain_expectations": _listify(matrix.get("domain_expectations")),
        "negative_signals": list(matrix.get("risk_blockers") or []),
        "hiring_constraints": [
            item
            for item in [
                matrix.get("location_requirements"),
                matrix.get("availability_requirements"),
            ]
            if item
        ],
        "interview_focus_areas": ["Validate supplied evidence for must-have and strong-signal requirements."],
        "confidence": 0.35,
        "missing_information": ["Gemini assisted insight disabled or unavailable."],
    }


def fallback_contextual_fit(row: dict[str, Any], *, model: str = DEFAULT_GEMINI_MODEL) -> dict[str, Any]:
    fit = float(row.get("fit_score") or 0)
    proof = float(row.get("proof_score") or 0)
    risk = float(row.get("risk_score") or 0)
    score = clamp_score((fit * 0.45) + (proof * 0.45) + ((100 - risk) * 0.10))
    ledger = row.get("evidence_ledger") or {}
    return {
        **ai_metadata(enabled=False, model=model, fallback_used=True),
        "contextual_fit_score": score,
        "semantic_fit_reason": "Deterministic fallback from fit, proof and risk scores because Gemini assisted insight is disabled or unavailable.",
        "hidden_strengths": _evidence_concepts(ledger.get("positive_evidence") or [], limit=3),
        "weak_context_signals": list(row.get("missing_evidence") or [])[:3],
        "evidence_supported": _evidence_snippets(ledger.get("positive_evidence") or [], limit=3),
        "evidence_missing": list(row.get("missing_evidence") or []),
        "risk_notes": [risk_item.get("explanation", "") for risk_item in row.get("risks", []) if isinstance(risk_item, dict)],
        "recommended_interview_checks": list(row.get("interview_focus") or [])[:5],
    }


def fallback_recruiter_explanation(row: dict[str, Any], *, model: str = DEFAULT_GEMINI_MODEL) -> dict[str, Any]:
    ledger = row.get("evidence_ledger") or {}
    positives = ledger.get("positive_evidence") or []
    missing = list(row.get("missing_evidence") or ledger.get("missing_evidence") or [])
    risks = row.get("risks") or []
    return {
        **ai_metadata(enabled=False, model=model, fallback_used=True),
        "executive_summary": row.get("main_reason") or "Missing from supplied data",
        "why_shortlisted": _listify((row.get("reasons") or {}).get("why_shortlisted")) or ["Missing from supplied data"],
        "strongest_evidence": _evidence_snippets(positives, limit=4) or ["Missing from supplied data"],
        "hidden_strengths": _evidence_concepts(positives, limit=4),
        "concerns": [risk.get("explanation", "Missing from supplied data") for risk in risks if isinstance(risk, dict)] or ["Missing from supplied data"],
        "missing_proof": missing or ["Missing from supplied data"],
        "interview_questions": [f"Verify: {item}" for item in (row.get("interview_focus") or missing or ["Missing from supplied data"])],
        "final_recruiter_note": "Gemini assisted insight disabled or unavailable; this explanation is deterministic and evidence-grounded.",
    }


def build_signal_fusion_summary(row: dict[str, Any], contextual_fit: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "role_fit": _score_label(row.get("fit_score")),
        "proof_strength": _score_label(row.get("proof_score")),
        "contextual_relevance": _score_label((contextual_fit or {}).get("contextual_fit_score")),
        "activity_or_behavioral_signal": _score_label(row.get("hireability_score")),
        "hireability": _score_label(row.get("hireability_score")),
        "risk": _risk_label(row.get("risk_score")),
        "summary": (
            f"Role fit {row.get('fit_score', 0):.0f}, proof {row.get('proof_score', 0):.0f}, "
            f"contextual relevance {(contextual_fit or {}).get('contextual_fit_score', 0):.0f}, "
            f"hireability {row.get('hireability_score', 0):.0f}, risk {row.get('risk_score', 0):.0f}."
        ),
    }


def detect_hidden_gem(row: dict[str, Any], all_rows: list[dict[str, Any]], contextual_fit: dict[str, Any] | None = None) -> dict[str, Any]:
    keyword_rank = _rank_by(all_rows, "fit_score", row.get("candidate_id"))
    proof_score = float(row.get("proof_score") or 0)
    risk_score = float(row.get("risk_score") or 0)
    contextual_score = float((contextual_fit or {}).get("contextual_fit_score") or 0)
    ledger = row.get("evidence_ledger") or {}
    proof_items = [
        item
        for item in ledger.get("positive_evidence", [])
        if isinstance(item, dict) and item.get("claim_or_proof") in {"proof", "strong_proof"}
    ]
    is_hidden = keyword_rank > 1 and proof_score >= 70 and contextual_score >= 70 and risk_score <= 20 and bool(proof_items)
    evidence = _evidence_snippets(proof_items, limit=3)
    return {
        "hidden_gem_candidate": is_hidden,
        "hidden_gem_reason": (
            "Strong proof and contextual relevance with low risk despite not leading on exact fit score."
            if is_hidden
            else "Hidden gem criteria not met: requires non-top exact fit, strong proof, strong contextual fit, low risk, and real work proof."
        ),
        "hidden_gem_evidence": evidence,
    }


def enrich_payload_with_fallback_ai(payload: dict[str, Any], *, model: str = DEFAULT_GEMINI_MODEL) -> dict[str, Any]:
    role_requirements = payload.get("role_requirements") or {}
    payload["ai_jd_insight"] = fallback_ai_jd_insight(role_requirements, model=model)
    rows = payload.get("rankings") or []
    for row in rows:
        contextual_fit = fallback_contextual_fit(row, model=model)
        row["ai_contextual_fit"] = contextual_fit
        row["ai_recruiter_explanation"] = fallback_recruiter_explanation(row, model=model)
        row.update(detect_hidden_gem(row, rows, contextual_fit))
        row["signal_fusion_summary"] = build_signal_fusion_summary(row, contextual_fit)
    return payload


def clamp_score(value: Any) -> int:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = 0.0
    return int(round(max(0.0, min(100.0, numeric))))


def _listify(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item]
    return [str(value)]


def _evidence_snippets(items: list[Any], *, limit: int) -> list[str]:
    snippets: list[str] = []
    for item in items:
        if isinstance(item, dict):
            snippet = item.get("snippet") or item.get("concept")
            if snippet:
                snippets.append(str(snippet))
    return snippets[:limit]


def _evidence_concepts(items: list[Any], *, limit: int) -> list[str]:
    concepts: list[str] = []
    for item in items:
        if isinstance(item, dict):
            concept = item.get("concept")
            if concept:
                concepts.append(str(concept))
    return concepts[:limit]


def _rank_by(rows: list[dict[str, Any]], field: str, candidate_id: str | None) -> int:
    ordered = sorted(rows, key=lambda item: (-(float(item.get(field) or 0)), str(item.get("candidate_id") or "")))
    for index, row in enumerate(ordered, start=1):
        if row.get("candidate_id") == candidate_id:
            return index
    return len(rows) + 1


def _score_label(value: Any) -> str:
    score = clamp_score(value)
    if score >= 75:
        return "strong"
    if score >= 50:
        return "moderate"
    return "weak"


def _risk_label(value: Any) -> str:
    score = clamp_score(value)
    if score >= 50:
        return "high"
    if score >= 20:
        return "review"
    return "low"
