from __future__ import annotations

from .models import ScoredCandidate
from .risk import build_risk_radar


def generate_reasoning(scored: ScoredCandidate) -> str:
    candidate = scored.candidate
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    features = scored.features

    strengths = [
        f"{features.current_title} with {features.years_of_experience:.1f} yrs",
    ]
    evidence = _display_evidence(features.evidence_phrases)
    if evidence:
        evidence_prefix = (
            "career evidence includes"
            if features.career_evidence_score > 0
            else "profile claims include"
        )
        strengths.append(f"{evidence_prefix} {_join_phrases(evidence[:3])}")
    elif features.relevant_skills:
        strengths.append(f"skills include {_join_phrases(features.relevant_skills[:3])}")

    practical_facts: list[str] = []
    location = profile.get("location")
    if location:
        practical_facts.append(str(location))
    if signals.get("recruiter_response_rate") is not None:
        response_rate = float(signals.get("recruiter_response_rate") or 0.0)
        if 1.0 < response_rate <= 100.0:
            response_rate /= 100.0
        practical_facts.append(f"response rate {response_rate:.2f}")
    if signals.get("notice_period_days") is not None:
        notice = max(int(signals.get("notice_period_days") or 0), 0)
        practical_facts.append(f"notice {notice} days")
    if practical_facts:
        strengths.append("; ".join(practical_facts))

    concerns = _concerns(features.risk_flags)
    if concerns:
        return f"{'; '.join(strengths)}. Concern: {_join_phrases(concerns)}."
    return f"{'; '.join(strengths)}."


def _concerns(flags: tuple[str, ...]) -> tuple[str, ...]:
    visible = [
        flag
        for flag in flags
        if flag
        in {
            "stale profile",
            "low recruiter response",
            "long notice period",
            "not marked open to work",
            "outside India",
            "non-target ML domain",
            "generic AI without shipped retrieval evidence",
            "keyword-stuffed profile",
            "expert skills with zero duration",
        }
    ]
    return tuple(visible[:3])


def _join_phrases(items: tuple[str, ...] | list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _display_evidence(phrases: tuple[str, ...]) -> tuple[str, ...]:
    labels: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        label = _evidence_label(phrase)
        key = label.lower()
        if key in seen:
            continue
        labels.append(label)
        seen.add(key)
    return tuple(labels)


def _evidence_label(phrase: str) -> str:
    if phrase in {"embedding", "embeddings", "embeddings-based"}:
        return "embeddings"
    if phrase in {"a/b testing", "a/b test", "ab test"}:
        return "A/B testing"
    if phrase in {"surface", "relevance"}:
        return "relevance systems"
    if phrase == "user intent":
        return "user-intent matching"
    if phrase == "ndcg":
        return "NDCG"
    if phrase == "mrr":
        return "MRR"
    if phrase == "map":
        return "MAP"
    return phrase


def generate_structured_reasoning(scored: ScoredCandidate, ledger: dict | None = None) -> dict:
    ledger = ledger or {}
    positive = ledger.get("positive_evidence", [])
    missing = ledger.get("missing_evidence", [])
    risks = build_risk_radar(scored)

    best_evidence = _best_evidence(positive)
    main_concern = _main_concern(risks, missing)
    why_shortlisted = _why_shortlisted(scored, best_evidence)
    why_not_higher = _why_not_ranked_higher(scored, missing, risks)
    interview_focus = ledger.get("interview_focus") or _fallback_interview_focus(scored, missing, risks)

    return {
        "why_shortlisted": why_shortlisted,
        "best_evidence": best_evidence,
        "main_concern": main_concern,
        "why_not_ranked_higher": why_not_higher,
        "interview_focus": interview_focus,
        "hiring_feasibility_summary": _hiring_feasibility(scored),
        "risk_summary": _risk_summary(risks),
    }


def _best_evidence(positive: list[dict]) -> list[str]:
    if not positive:
        return ["Unclear: no positive evidence was extracted from supplied fields."]
    ordered = sorted(
        positive,
        key=lambda item: (
            {"strong_proof": 3, "proof": 2, "claim": 1}.get(item.get("claim_or_proof", ""), 0),
            item.get("score_impact", 0),
        ),
        reverse=True,
    )
    return [f"{item['concept']}: {item['snippet']}" for item in ordered[:3]]


def _main_concern(risks: list[dict], missing: list[str]) -> str:
    if risks:
        return f"{risks[0]['risk_type']}: {risks[0]['explanation']}"
    if missing:
        return f"Missing evidence: {missing[0]}"
    return "No major concern from supplied fields."


def _why_shortlisted(scored: ScoredCandidate, best_evidence: list[str]) -> str:
    features = scored.features
    if features.evidence_concepts:
        return (
            f"{features.current_title or 'Candidate'} has role-relevant evidence in "
            f"{_join_phrases(list(features.evidence_concepts[:3]))} with product score "
            f"{scored.product_scores.final_score:.1f}."
        )
    if features.relevant_skills:
        return (
            f"{features.current_title or 'Candidate'} lists relevant skills "
            f"{_join_phrases(list(features.relevant_skills[:3]))}, but proof depth should be verified."
        )
    return best_evidence[0] if best_evidence else "Shortlist rationale is unclear from supplied fields."


def _why_not_ranked_higher(scored: ScoredCandidate, missing: list[str], risks: list[dict]) -> str:
    if risks:
        return f"Risk pressure from {risks[0]['risk_type']} reduces rank confidence."
    if missing:
        return f"Could rank higher with clearer {missing[0]}."
    if scored.product_scores.final_score >= 95:
        return "Already near the top; ranking depends on fine-grained evidence strength."
    return "Additional production impact details could improve confidence."


def _fallback_interview_focus(scored: ScoredCandidate, missing: list[str], risks: list[dict]) -> list[str]:
    focus: list[str] = []
    if scored.features.evidence_concepts:
        focus.append(f"Ask for architecture and metrics behind {scored.features.evidence_concepts[0]}.")
    if missing:
        focus.append(f"Verify {missing[0]}.")
    if risks:
        focus.append(f"Probe {risks[0]['risk_type']}.")
    return focus or ["Confirm shipped ownership, team scope, and current availability."]


def _hiring_feasibility(scored: ScoredCandidate) -> str:
    features = scored.features
    facts: list[str] = []
    if features.location:
        facts.append(features.location)
    if features.availability_score > 7:
        facts.append("strong availability signals")
    elif features.availability_score <= 2:
        facts.append("weak availability signals")
    if features.logistics_score > 4:
        facts.append("good logistics fit")
    elif features.logistics_score <= 1:
        facts.append("logistics risk")
    return "; ".join(facts) if facts else "Hiring feasibility is unclear from supplied fields."


def _risk_summary(risks: list[dict]) -> str:
    if not risks:
        return "No structured risk flags from supplied fields."
    return _join_phrases([f"{risk['risk_type']} ({risk['severity']})" for risk in risks[:3]])
