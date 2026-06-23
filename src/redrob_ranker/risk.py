from __future__ import annotations

from typing import Mapping

from .job_understanding import RoleRequirementMatrix
from .models import ScoredCandidate


FLAG_TO_RISK = {
    "keyword-stuffed profile": ("keyword stuffing", "high"),
    "expert skills with zero duration": ("weak proof behind strong claims", "medium"),
    "generic AI without shipped retrieval evidence": ("weak proof behind strong claims", "high"),
    "non-target ML domain": ("non target domain", "medium"),
    "outside India": ("location mismatch", "high"),
    "not marked open to work": ("negative availability", "medium"),
    "stale profile": ("stale activity", "medium"),
    "low recruiter response": ("low recruiter response", "medium"),
    "long notice period": ("long notice period", "medium"),
    "missing last active date": ("incomplete profile", "low"),
}


def build_risk_radar(
    scored: ScoredCandidate,
    role_requirements: RoleRequirementMatrix | None = None,
) -> list[dict]:
    features = scored.features
    risks: list[dict] = []
    for flag in features.risk_flags:
        risk_type, severity = FLAG_TO_RISK.get(flag, ("missing important evidence", "low"))
        risks.append(_risk_item(risk_type, severity, flag, _score_impact(severity), _explanation_for_flag(flag)))
        if flag == "generic AI without shipped retrieval evidence":
            risks.append(
                _risk_item(
                    "inflated AI style claims",
                    "medium",
                    flag,
                    -6.0,
                    "Profile emphasizes AI tooling or demos without enough shipped retrieval proof.",
                )
            )
        if flag == "outside India" and not _willing_to_relocate(scored.candidate):
            risks.append(
                _risk_item(
                    "unwilling relocation",
                    "high",
                    "outside India and relocation not confirmed",
                    -12.0,
                    "Location appears outside the target geography and relocation willingness is not positive.",
                )
            )

    if features.retrieval_quality_score + features.ranking_quality_score + features.evaluation_quality_score < 1.0:
        risks.append(
            _risk_item(
                "missing important evidence",
                "high",
                "little or no career-backed retrieval/ranking/evaluation evidence",
                -12.0,
                "The profile does not provide enough role-critical proof in career history.",
            )
        )
    if features.relevant_skill_count >= 5 and features.career_evidence_score <= 1:
        risks.append(
            _risk_item(
                "weak proof behind strong claims",
                "medium",
                "skills list is stronger than career evidence",
                -6.0,
                "Listed skills are not sufficiently backed by work-history proof.",
            )
        )
    if _profile_completeness(scored.candidate) < 50:
        risks.append(
            _risk_item(
                "incomplete profile",
                "low",
                "profile completeness below 50",
                -2.0,
                "Missing profile fields reduce confidence but are not treated as disqualifying.",
            )
        )

    if role_requirements:
        lower_text = str(scored.candidate).casefold()
        for blocker in role_requirements.risk_blockers:
            if blocker.casefold() in lower_text:
                risks.append(
                    _risk_item(
                        "risk blocker",
                        "high",
                        blocker,
                        -10.0,
                        "Candidate text matches a blocker listed in the job description.",
                    )
                )

    return _dedupe_risks(risks)


def _risk_item(risk_type: str, severity: str, evidence: str, score_impact: float, explanation: str) -> dict:
    return {
        "risk_type": risk_type,
        "severity": severity,
        "evidence": evidence,
        "score_impact": score_impact,
        "explanation": explanation,
    }


def _score_impact(severity: str) -> float:
    return {"high": -12.0, "medium": -6.0, "low": -2.0}.get(severity, -2.0)


def _explanation_for_flag(flag: str) -> str:
    explanations = {
        "keyword-stuffed profile": "Many role keywords appear without matching career proof.",
        "expert skills with zero duration": "Expert-level skill claims have no duration support.",
        "generic AI without shipped retrieval evidence": "AI claims appear demo-heavy and lack shipped retrieval proof.",
        "non-target ML domain": "Relevant ML background appears concentrated outside the target search/ranking domain.",
        "outside India": "Location does not match the target geography.",
        "not marked open to work": "Availability is weaker because the candidate is not marked open to work.",
        "stale profile": "Recent activity is weak.",
        "low recruiter response": "Historical recruiter response rate is low.",
        "long notice period": "Notice period may slow hiring.",
        "missing last active date": "Recent activity could not be verified.",
    }
    return explanations.get(flag, "Potential issue detected from candidate fields.")


def _willing_to_relocate(candidate: Mapping) -> bool:
    signals = candidate.get("redrob_signals", {})
    return bool(isinstance(signals, Mapping) and signals.get("willing_to_relocate"))


def _profile_completeness(candidate: Mapping) -> float:
    signals = candidate.get("redrob_signals", {})
    if isinstance(signals, Mapping):
        try:
            return float(signals.get("profile_completeness_score", 100.0))
        except (TypeError, ValueError):
            return 100.0
    return 100.0


def _dedupe_risks(risks: list[dict]) -> list[dict]:
    result: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for risk in risks:
        key = (risk["risk_type"], risk["evidence"])
        if key in seen:
            continue
        seen.add(key)
        result.append(risk)
    return result

