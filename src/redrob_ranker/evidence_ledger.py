from __future__ import annotations

from typing import Iterable, Mapping

from .models import ScoredCandidate
from .risk import build_risk_radar


def build_evidence_ledger(scored: ScoredCandidate, rank: int) -> dict:
    features = scored.features
    positive = _positive_evidence(scored)
    negative = _negative_evidence(scored)
    missing = _missing_evidence(scored)
    risks = build_risk_radar(scored)
    source_fields = sorted({item["source_field"] for item in [*positive, *negative] if item.get("source_field")})

    return {
        "candidate_id": scored.candidate_id,
        "rank": rank,
        "final_score": scored.product_scores.final_score,
        "fit_score": scored.product_scores.fit_score,
        "proof_score": scored.product_scores.proof_score,
        "confidence_score": scored.product_scores.confidence_score,
        "hireability_score": scored.product_scores.hireability_score,
        "risk_score": scored.product_scores.risk_score,
        "positive_evidence": positive,
        "negative_evidence": negative,
        "missing_evidence": missing,
        "risk_flags": risks,
        "source_fields": source_fields,
        "score_impacts": _score_impacts(scored),
        "interview_focus": _interview_focus(scored, missing, risks),
        "explanation": _ledger_explanation(scored, positive, risks),
    }


def _positive_evidence(scored: ScoredCandidate) -> list[dict]:
    candidate = scored.candidate
    evidence: list[dict] = []
    for skill in scored.features.relevant_skills[:8]:
        evidence.append(
            _evidence_item(
                evidence_type="skill",
                concept=skill,
                source_field="skills",
                snippet=f"Candidate lists {skill} in skills.",
                strength="medium",
                confidence=0.55,
                polarity="positive",
                claim_or_proof="claim",
                score_impact=1.0,
            )
        )

    for index, item in enumerate(_history(candidate)):
        description = str(item.get("description", ""))
        title = str(item.get("title", ""))
        source_field = f"career_history[{index}].description"
        matched = [
            phrase
            for phrase in scored.features.evidence_phrases
            if phrase and phrase.casefold() in f"{title} {description}".casefold()
        ]
        if not matched:
            continue
        claim_type = "strong_proof" if _has_production_context(description) else "proof"
        strength = "high" if claim_type == "strong_proof" else "medium"
        for phrase in matched[:4]:
            evidence.append(
                _evidence_item(
                    evidence_type="career_evidence",
                    concept=phrase,
                    source_field=source_field,
                    snippet=_snippet(description, phrase),
                    strength=strength,
                    confidence=0.85 if claim_type == "strong_proof" else 0.72,
                    polarity="positive",
                    claim_or_proof=claim_type,
                    score_impact=2.5 if claim_type == "strong_proof" else 1.6,
                )
            )

    profile = candidate.get("profile", {})
    if isinstance(profile, Mapping):
        profile_text = " ".join(str(profile.get(key, "")) for key in ("headline", "summary", "current_title"))
        for phrase in scored.features.evidence_phrases:
            if phrase.casefold() in profile_text.casefold() and not any(item["concept"] == phrase for item in evidence):
                evidence.append(
                    _evidence_item(
                        evidence_type="profile_claim",
                        concept=phrase,
                        source_field="profile.summary",
                        snippet=_snippet(profile_text, phrase),
                        strength="low",
                        confidence=0.45,
                        polarity="positive",
                        claim_or_proof="claim",
                        score_impact=0.6,
                    )
                )
    return evidence[:24]


def _negative_evidence(scored: ScoredCandidate) -> list[dict]:
    return [
        _evidence_item(
            evidence_type="risk",
            concept=flag,
            source_field="redrob_signals/profile",
            snippet=flag,
            strength="medium",
            confidence=0.7,
            polarity="negative",
            claim_or_proof="proof",
            score_impact=-4.0,
        )
        for flag in scored.features.risk_flags
    ]


def _missing_evidence(scored: ScoredCandidate) -> list[str]:
    missing: list[str] = []
    features = scored.features
    if features.retrieval_quality_score <= 0:
        missing.append("career-backed retrieval proof")
    if features.ranking_quality_score <= 0:
        missing.append("career-backed ranking proof")
    if features.evaluation_quality_score <= 0:
        missing.append("evaluation methodology or ranking metrics")
    if features.production_score <= 1:
        missing.append("production ownership details")
    if not features.relevant_skills:
        missing.append("role-relevant skills")
    return missing


def _score_impacts(scored: ScoredCandidate) -> dict:
    c = scored.components
    return {
        "fit": round(c.role + c.seniority + c.retrieval + c.ranking + c.evaluation + c.skills, 2),
        "proof": round(c.retrieval + c.ranking + c.evaluation + c.production + c.engineering, 2),
        "confidence": round(c.confidence, 2),
        "hireability": round(c.availability + c.logistics + c.leadership, 2),
        "risk_penalty": round(-c.risk, 2),
    }


def _interview_focus(scored: ScoredCandidate, missing: list[str], risks: list[dict]) -> list[str]:
    focus = []
    if scored.features.evidence_concepts:
        focus.append(f"Validate depth of {scored.features.evidence_concepts[0]} work.")
    if missing:
        focus.append(f"Ask for evidence of {missing[0]}.")
    if risks:
        focus.append(f"Clarify risk: {risks[0]['risk_type']}.")
    if not focus:
        focus.append("Confirm recent production ownership and team scope.")
    return focus[:3]


def _ledger_explanation(scored: ScoredCandidate, positive: list[dict], risks: list[dict]) -> str:
    if positive:
        lead = positive[0]["snippet"]
    else:
        lead = "Role evidence is unclear from supplied candidate fields."
    if risks:
        return f"{lead} Main risk: {risks[0]['risk_type']}."
    return lead


def _history(candidate: Mapping) -> Iterable[Mapping]:
    history = candidate.get("career_history", [])
    return history if isinstance(history, list) else []


def _has_production_context(text: str) -> bool:
    lower = text.casefold()
    return any(term in lower for term in ("shipped", "production", "deployed", "serving", "owned", "launched"))


def _snippet(text: str, phrase: str, window: int = 140) -> str:
    if not text:
        return "Unclear from supplied fields."
    lower = text.casefold()
    index = lower.find(phrase.casefold())
    if index == -1:
        return text[:window].strip()
    start = max(index - 45, 0)
    end = min(index + len(phrase) + 85, len(text))
    return text[start:end].strip()


def _evidence_item(
    *,
    evidence_type: str,
    concept: str,
    source_field: str,
    snippet: str,
    strength: str,
    confidence: float,
    polarity: str,
    claim_or_proof: str,
    score_impact: float,
) -> dict:
    return {
        "evidence_type": evidence_type,
        "concept": concept,
        "source_field": source_field,
        "snippet": snippet or "Unclear from supplied fields.",
        "strength": strength,
        "confidence": confidence,
        "polarity": polarity,
        "claim_or_proof": claim_or_proof,
        "score_impact": score_impact,
    }

