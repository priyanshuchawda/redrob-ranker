from __future__ import annotations

from datetime import date
from typing import Iterable, Mapping

from .features import extract_features
from .models import RankedCandidate, ScoredCandidate
from .reasoning import generate_reasoning


def score_candidate(candidate: Mapping, reference_date: date | None = None) -> ScoredCandidate:
    features = extract_features(candidate, reference_date=reference_date)
    score = (
        features.role_score * 5.0
        + features.seniority_score * 3.0
        + min(features.retrieval_evidence, 8) * 3.0
        + min(features.ranking_evidence, 6) * 3.0
        + min(features.evaluation_evidence, 5) * 2.2
        + min(features.relevant_skill_count, 10) * 1.2
        + min(features.product_company_months / 12.0, 9.0) * 1.4
        + features.availability_score * 2.2
        + features.logistics_score * 2.0
        - features.risk_penalty
    )
    return ScoredCandidate(
        candidate_id=features.candidate_id,
        score=round(score, 6),
        candidate=dict(candidate),
        features=features,
    )


def rank_candidates(
    candidates: Iterable[Mapping],
    reference_date: date | None = None,
    top_n: int = 100,
) -> list[RankedCandidate]:
    scored = [score_candidate(candidate, reference_date=reference_date) for candidate in candidates]
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

