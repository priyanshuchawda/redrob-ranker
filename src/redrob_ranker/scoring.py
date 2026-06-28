from __future__ import annotations

from datetime import date
import heapq
import re
from dataclasses import replace
from typing import Iterable, Mapping

from .config import DEFAULT_WEIGHTS, ScoringWeights
from .fairness import strip_protected_attributes
from .features import extract_features
from .job_understanding import RoleRequirementMatrix
from .models import CandidateFeatures, ProductScores, RankedCandidate, ScoreComponents, ScoredCandidate
from .reasoning import generate_reasoning


def score_candidate(
    candidate: Mapping,
    reference_date: date | None = None,
    role_requirements: RoleRequirementMatrix | None = None,
) -> ScoredCandidate:
    cleaned_candidate, _ignored = strip_protected_attributes(dict(candidate))
    features = extract_features(cleaned_candidate, reference_date=reference_date)
    if not features.candidate_id:
        raise ValueError("Candidate record is missing a non-empty candidate_id")
    components = score_components(features)
    if role_requirements is not None:
        components = apply_role_requirements_adjustments(components, features, cleaned_candidate, role_requirements)
    product_scores = normalize_product_scores(components, features)
    return ScoredCandidate(
        candidate_id=features.candidate_id,
        score=components.total,
        candidate=dict(cleaned_candidate),
        features=features,
        components=components,
        product_scores=product_scores,
    )


def score_components(
    features: CandidateFeatures,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
) -> ScoreComponents:
    role = features.role_score * weights.role
    seniority = features.seniority_score * weights.seniority
    retrieval = min(features.retrieval_quality_score, 8.0) * weights.retrieval
    ranking = min(features.ranking_quality_score, 6.0) * weights.ranking
    evaluation = min(features.evaluation_quality_score, 5.0) * weights.evaluation
    profile_evidence = min(features.profile_evidence_score, 8.0) * weights.profile_evidence
    skills = min(features.skill_trust_score, 18.0) * weights.skills
    product = min(features.product_company_months / 12.0, 9.0) * weights.product_experience
    production = features.production_score * weights.production
    engineering = features.engineering_score * weights.engineering
    leadership = features.leadership_score * weights.leadership
    confidence = features.evidence_confidence * weights.confidence
    availability = features.availability_score * weights.availability
    logistics = features.logistics_score * weights.logistics
    quality_total = (
        features.retrieval_quality_score
        + features.ranking_quality_score
        + features.evaluation_quality_score
    )
    evidence_gap_penalty = (
        weights.severe_evidence_gap
        if quality_total < 1.0
        else weights.moderate_evidence_gap
        if quality_total < 2.5
        else 0.0
    )
    risk = features.risk_penalty + evidence_gap_penalty
    total = (
        role
        + seniority
        + retrieval
        + ranking
        + evaluation
        + profile_evidence
        + skills
        + product
        + production
        + engineering
        + leadership
        + confidence
        + availability
        + logistics
        - risk
    )
    return ScoreComponents(
        role=round(role, 6),
        seniority=round(seniority, 6),
        retrieval=round(retrieval, 6),
        ranking=round(ranking, 6),
        evaluation=round(evaluation, 6),
        profile_evidence=round(profile_evidence, 6),
        skills=round(skills, 6),
        product=round(product, 6),
        production=round(production, 6),
        engineering=round(engineering, 6),
        leadership=round(leadership, 6),
        confidence=round(confidence, 6),
        availability=round(availability, 6),
        logistics=round(logistics, 6),
        risk=round(risk, 6),
        total=round(total, 6),
    )


def score_candidates(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
    role_requirements: RoleRequirementMatrix | None = None,
) -> list[ScoredCandidate]:
    scored: list[ScoredCandidate] = []
    seen_ids: set[str] = set()
    for candidate in candidates:
        item = score_candidate(candidate, reference_date=reference_date, role_requirements=role_requirements)
        if item.candidate_id in seen_ids:
            raise ValueError(f"Duplicate candidate_id: {item.candidate_id}")
        seen_ids.add(item.candidate_id)
        scored.append(item)
    return scored


def rank_candidates(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
    top_n: int = 100,
    role_requirements: RoleRequirementMatrix | None = None,
) -> list[RankedCandidate]:
    return rank_scored_candidates(
        score_candidates(candidates, reference_date=reference_date, role_requirements=role_requirements),
        top_n=top_n,
    )


def rank_candidates_streaming(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
    top_n: int = 100,
    role_requirements: RoleRequirementMatrix | None = None,
) -> list[RankedCandidate]:
    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")

    heap: list[tuple[float, tuple[int, ...], ScoredCandidate]] = []
    seen_ids: set[str] = set()
    for candidate in candidates:
        item = score_candidate(candidate, reference_date=reference_date, role_requirements=role_requirements)
        if item.candidate_id in seen_ids:
            raise ValueError(f"Duplicate candidate_id: {item.candidate_id}")
        seen_ids.add(item.candidate_id)
        heap_key = (item.score, _reverse_lex_key(item.candidate_id))
        entry = (*heap_key, item)
        if len(heap) < top_n:
            heapq.heappush(heap, entry)
        elif heap_key > heap[0][:2]:
            heapq.heapreplace(heap, entry)

    if len(heap) < top_n:
        raise ValueError(f"requested top_n {top_n}, but only {len(heap)} candidates were loaded")

    top_scored = [entry[2] for entry in heap]
    return rank_scored_candidates(top_scored, top_n=top_n)


def rank_scored_candidates(
    scored: Iterable[ScoredCandidate],
    top_n: int = 100,
) -> list[RankedCandidate]:
    if top_n <= 0:
        raise ValueError("top_n must be greater than zero")
    scored = list(scored)
    scored.sort(key=lambda item: (-item.score, item.candidate_id))

    ranked: list[RankedCandidate] = []
    for rank, item in enumerate(scored[:top_n], start=1):
        ranked.append(
            RankedCandidate(
                candidate_id=item.candidate_id,
                rank=rank,
                score=item.score,
                reasoning=generate_reasoning(item),
            )
        )
    return ranked


def _reverse_lex_key(value: str) -> tuple[int, ...]:
    return tuple(-ord(char) for char in value)


def apply_role_requirements_adjustments(
    components: ScoreComponents,
    features: CandidateFeatures,
    candidate: Mapping,
    role_requirements: RoleRequirementMatrix,
) -> ScoreComponents:
    text = _candidate_text(candidate)
    skill_text = " ".join(features.relevant_skills).casefold()
    must_have_hits = sum(_contains_term(text, skill) or skill.casefold() in skill_text for skill in role_requirements.must_have_skills)
    strong_hits = sum(_contains_term(text, skill) for skill in role_requirements.strong_signal_skills)
    good_hits = sum(_contains_term(text, skill) or skill.casefold() in skill_text for skill in role_requirements.good_to_have_skills)

    must_have_total = max(len(role_requirements.must_have_skills), 1)
    fit_boost = min((must_have_hits / must_have_total) * 6.0 + strong_hits * 0.8 + good_hits * 0.35, 10.0)

    seniority_adjustment = _seniority_adjustment(features.years_of_experience, role_requirements.seniority_expectations)
    production_adjustment = 2.0 if role_requirements.production_expectations and features.production_score >= 3.0 else 0.0
    domain_adjustment = 2.0 if _domain_matches(text, role_requirements.domain_expectations) else 0.0
    location_adjustment = _location_adjustment(features.location, features.country, role_requirements.location_requirements)
    availability_adjustment = _availability_adjustment(candidate, role_requirements.availability_requirements)
    blocker_penalty = _blocker_penalty(text, role_requirements.risk_blockers)

    role = components.role + fit_boost * 0.35
    seniority = components.seniority + seniority_adjustment
    skills = components.skills + fit_boost
    production = components.production + production_adjustment
    product = components.product + domain_adjustment
    logistics = components.logistics + location_adjustment
    availability = components.availability + availability_adjustment
    risk = components.risk + blocker_penalty
    total = (
        role
        + seniority
        + components.retrieval
        + components.ranking
        + components.evaluation
        + components.profile_evidence
        + skills
        + product
        + production
        + components.engineering
        + components.leadership
        + components.confidence
        + availability
        + logistics
        - risk
    )
    return replace(
        components,
        role=round(role, 6),
        seniority=round(seniority, 6),
        skills=round(skills, 6),
        product=round(product, 6),
        production=round(production, 6),
        availability=round(availability, 6),
        logistics=round(logistics, 6),
        risk=round(risk, 6),
        total=round(total, 6),
    )


def normalize_product_scores(components: ScoreComponents, features: CandidateFeatures) -> ProductScores:
    fit_raw = (
        max(components.role, 0)
        + max(components.seniority, 0)
        + max(components.retrieval, 0)
        + max(components.ranking, 0)
        + max(components.evaluation, 0)
        + max(components.skills, 0)
        + max(components.product, 0)
    )
    proof_raw = (
        max(components.retrieval, 0)
        + max(components.ranking, 0)
        + max(components.evaluation, 0)
        + max(components.production, 0)
        + max(components.engineering, 0)
    )
    hireability_raw = max(components.availability, 0) + max(components.logistics, 0) + max(components.leadership, 0)
    risk_score = _clamp(components.risk * 2.0, 0.0, 100.0)
    final_score = _clamp((components.total / 160.0) * 100.0, 0.0, 100.0)
    return ProductScores(
        final_score=round(final_score, 2),
        fit_score=round(_clamp(fit_raw / 95.0 * 100.0, 0.0, 100.0), 2),
        proof_score=round(_clamp(proof_raw / 75.0 * 100.0, 0.0, 100.0), 2),
        confidence_score=round(_clamp(components.confidence / 9.0 * 100.0, 0.0, 100.0), 2),
        hireability_score=round(_clamp(hireability_raw / 30.0 * 100.0, 0.0, 100.0), 2),
        risk_score=round(risk_score, 2),
    )


def _candidate_text(candidate: Mapping) -> str:
    chunks: list[str] = []

    def collect(value: object) -> None:
        if isinstance(value, Mapping):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
        elif isinstance(value, str):
            chunks.append(value)

    collect(candidate)
    return " ".join(chunks).casefold()


def _contains_term(text: str, term: str) -> bool:
    normalized = term.casefold().strip()
    if not normalized:
        return False
    return normalized in text


def _seniority_adjustment(years: float, expectation: str) -> float:
    match = re.search(r"(\d+)\s*[-+]\s*(\d+)?", expectation)
    if not match:
        return 0.0
    lower = float(match.group(1))
    upper = float(match.group(2) or lower + 2)
    if lower <= years <= upper:
        return 2.0
    if lower - 1 <= years <= upper + 2:
        return 0.5
    return -2.0


def _domain_matches(text: str, expectation: str) -> bool:
    terms = [term for term in re.split(r"[^a-zA-Z0-9+#]+", expectation.casefold()) if len(term) >= 5]
    if not terms:
        return False
    hits = sum(term in text for term in terms)
    return hits >= min(2, len(terms))


def _location_adjustment(location: str, country: str, requirements: str) -> float:
    if not requirements:
        return 0.0
    req = requirements.casefold()
    loc = f"{location} {country}".casefold()
    cities = ("pune", "bangalore", "bengaluru", "delhi", "noida", "gurgaon", "gurugram", "mumbai", "hyderabad", "india")
    if any(city in req and city in loc for city in cities):
        return 1.5
    if "india" in req and "india" not in loc:
        return -3.0
    return 0.0


def _availability_adjustment(candidate: Mapping, requirements: str) -> float:
    if not requirements:
        return 0.0
    signals = candidate.get("redrob_signals", {})
    notice = signals.get("notice_period_days") if isinstance(signals, Mapping) else None
    match = re.search(r"(\d+)\s*days?", requirements)
    if match and notice is not None:
        return 1.0 if int(notice or 0) <= int(match.group(1)) else -2.0
    return 0.0


def _blocker_penalty(text: str, blockers: list[str]) -> float:
    penalty = 0.0
    for blocker in blockers:
        normalized = blocker.casefold()
        if normalized and normalized in text:
            penalty += 8.0
    return min(penalty, 24.0)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))
