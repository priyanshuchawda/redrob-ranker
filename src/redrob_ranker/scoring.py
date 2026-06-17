from __future__ import annotations

from datetime import date
from typing import Iterable, Mapping

from .features import extract_features
from .models import CandidateFeatures, RankedCandidate, ScoreComponents, ScoredCandidate
from .reasoning import generate_reasoning


def score_candidate(candidate: Mapping, reference_date: date | None = None) -> ScoredCandidate:
    features = extract_features(candidate, reference_date=reference_date)
    components = score_components(features)
    return ScoredCandidate(
        candidate_id=features.candidate_id,
        score=components.total,
        candidate=dict(candidate),
        features=features,
        components=components,
    )


def score_components(features: CandidateFeatures) -> ScoreComponents:
    role = features.role_score * 5.0
    seniority = features.seniority_score * 3.0
    retrieval = min(features.retrieval_evidence, 8) * 3.0
    ranking = min(features.ranking_evidence, 6) * 3.0
    evaluation = min(features.evaluation_evidence, 5) * 2.2
    skills = min(features.relevant_skill_count, 10) * 1.2
    product = min(features.product_company_months / 12.0, 9.0) * 1.4
    availability = features.availability_score * 2.2
    logistics = features.logistics_score * 2.0
    risk = features.risk_penalty
    total = role + seniority + retrieval + ranking + evaluation + skills + product + availability + logistics - risk
    return ScoreComponents(
        role=round(role, 6),
        seniority=round(seniority, 6),
        retrieval=round(retrieval, 6),
        ranking=round(ranking, 6),
        evaluation=round(evaluation, 6),
        skills=round(skills, 6),
        product=round(product, 6),
        availability=round(availability, 6),
        logistics=round(logistics, 6),
        risk=round(risk, 6),
        total=round(total, 6),
    )


def score_candidates(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
) -> list[ScoredCandidate]:
    return [score_candidate(candidate, reference_date=reference_date) for candidate in candidates]


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
