from __future__ import annotations

from datetime import date

from redrob_ranker.features import extract_features
from tests.fixtures import base_candidate, keyword_stuffed_candidate, stale_candidate


def test_extracts_production_retrieval_and_ranking_evidence() -> None:
    features = extract_features(base_candidate(), reference_date=date(2026, 6, 17))

    assert features.candidate_id == "CAND_0000001"
    assert features.role_score >= 4.0
    assert features.retrieval_evidence >= 5
    assert features.ranking_evidence >= 3
    assert features.evaluation_evidence >= 3
    assert features.product_company_months >= 80
    assert features.relevant_skill_count >= 7
    assert "Python" in features.relevant_skills
    assert "hybrid search" in features.evidence_phrases


def test_detects_keyword_stuffed_non_ml_profile() -> None:
    features = extract_features(keyword_stuffed_candidate(), reference_date=date(2026, 6, 17))

    assert features.role_score < 0
    assert features.retrieval_evidence == 0
    assert features.ranking_evidence == 0
    assert features.keyword_stuffing_risk is True
    assert "expert skills with zero duration" in features.risk_flags


def test_behavioral_availability_scores_recent_responsive_candidates_higher() -> None:
    active = extract_features(base_candidate(), reference_date=date(2026, 6, 17))
    stale = extract_features(stale_candidate(), reference_date=date(2026, 6, 17))

    assert active.availability_score > stale.availability_score
    assert active.availability_score >= 8.0
    assert stale.availability_score <= 3.0
    assert "stale profile" in stale.risk_flags


def test_junior_ml_title_is_not_treated_as_senior_fit() -> None:
    candidate = base_candidate()
    candidate["profile"]["current_title"] = "Junior ML Engineer"

    features = extract_features(candidate, reference_date=date(2026, 6, 17))

    assert features.role_score <= 2.0
