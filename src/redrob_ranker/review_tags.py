from __future__ import annotations

from typing import Mapping

from .models import ScoredCandidate


def generate_review_tags(scored: ScoredCandidate, ledger: Mapping | None = None) -> list[str]:
    """Return short deterministic recruiter review tags grounded in existing score/evidence fields."""

    ledger = ledger or {}
    missing = {str(item).casefold() for item in ledger.get("missing_evidence", [])}
    risk_text = " ".join(scored.features.risk_flags).casefold()
    tags: list[str] = []

    if scored.features.production_score <= 1 or any("production" in item for item in missing):
        tags.append("Missing production proof")
    if scored.features.ranking_quality_score <= 0 or any("ranking" in item for item in missing):
        tags.append("Weak career backed ranking evidence")
    if scored.product_scores.confidence_score < 45:
        tags.append("Low confidence")
    if "outside india" in risk_text or scored.product_scores.hireability_score < 35:
        tags.append("Location risk")
    if any(flag in risk_text for flag in ("not marked open", "stale profile", "long notice", "low recruiter response")):
        tags.append("Availability risk")
    if scored.features.keyword_stuffing_risk or "generic ai without shipped retrieval evidence" in risk_text:
        tags.append("Strong claims but weak proof")
    if scored.features.evaluation_quality_score <= 0 or any("evaluation" in item for item in missing):
        tags.append("Good fit but missing evaluation evidence")
    if scored.product_scores.risk_score >= 50:
        tags.append("High risk profile")

    if not tags:
        tags.append("No major blocker")
    return list(dict.fromkeys(tags))[:4]


def primary_review_tag(scored: ScoredCandidate, ledger: Mapping | None = None) -> str:
    return generate_review_tags(scored, ledger)[0]
