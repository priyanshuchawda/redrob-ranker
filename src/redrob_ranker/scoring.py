from __future__ import annotations

from datetime import date
from typing import Iterable, Mapping

from .config import DEFAULT_WEIGHTS, ScoringWeights
from .features import extract_features
from .models import CandidateFeatures, RankedCandidate, ScoreComponents, ScoredCandidate
from .reasoning import generate_reasoning


def score_candidate(candidate: Mapping, reference_date: date | None = None) -> ScoredCandidate:
    features = extract_features(candidate, reference_date=reference_date)
    if not features.candidate_id:
        raise ValueError("Candidate record is missing a non-empty candidate_id")
    components = score_components(features)
    return ScoredCandidate(
        candidate_id=features.candidate_id,
        score=components.total,
        candidate=dict(candidate),
        features=features,
        components=components,
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
) -> list[ScoredCandidate]:
    scored: list[ScoredCandidate] = []
    seen_ids: set[str] = set()
    for candidate in candidates:
        item = score_candidate(candidate, reference_date=reference_date)
        if item.candidate_id in seen_ids:
            raise ValueError(f"Duplicate candidate_id: {item.candidate_id}")
        seen_ids.add(item.candidate_id)
        scored.append(item)
    return scored


def rank_candidates(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
    top_n: int = 100,
) -> list[RankedCandidate]:
    return rank_scored_candidates(score_candidates(candidates, reference_date=reference_date), top_n=top_n)


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
