from __future__ import annotations

from .models import ScoredCandidate


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
