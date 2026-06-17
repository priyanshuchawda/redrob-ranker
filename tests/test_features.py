from __future__ import annotations

from datetime import date

from redrob_ranker.features import extract_features
from tests.fixtures import (
    base_candidate,
    keyword_stuffed_candidate,
    generic_ai_keyword_candidate,
    outside_india_candidate,
    plain_language_matching_candidate,
    semantic_matching_candidate,
    stale_candidate,
)


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


def test_extracts_plain_language_relevance_system_evidence() -> None:
    features = extract_features(plain_language_matching_candidate(), reference_date=date(2026, 6, 17))

    assert features.retrieval_evidence >= 3
    assert features.ranking_evidence >= 2
    assert features.evaluation_evidence >= 2
    assert "matching layer" in features.evidence_phrases
    assert "Ranking Systems" in features.relevant_skills


def test_outside_india_is_a_material_logistics_risk() -> None:
    features = extract_features(outside_india_candidate(), reference_date=date(2026, 6, 17))

    assert features.logistics_score <= 1.0
    assert "outside India" in features.risk_flags
    assert features.risk_penalty >= 8.0


def test_extracts_hiring_search_relevance_patterns() -> None:
    features = extract_features(semantic_matching_candidate(), reference_date=date(2026, 6, 17))

    assert features.retrieval_evidence >= 8
    assert features.ranking_evidence >= 5
    assert features.evaluation_evidence >= 2
    assert "candidate matching" in features.evidence_phrases
    assert "two-tower" in features.evidence_phrases
    assert "cross encoder" in features.evidence_phrases
    assert "retrieval evaluation" in features.evidence_phrases
    assert "Two-Tower Models" in features.relevant_skills


def test_detects_generic_ai_without_shipped_retrieval_evidence() -> None:
    features = extract_features(generic_ai_keyword_candidate(), reference_date=date(2026, 6, 17))

    assert "generic AI without shipped retrieval evidence" in features.risk_flags
    assert features.risk_penalty >= 15.0
