from __future__ import annotations

from datetime import date

from redrob_ranker.features import extract_features
from tests.fixtures import (
    base_candidate,
    keyword_stuffed_candidate,
    generic_ai_keyword_candidate,
    outside_india_candidate,
    plain_language_matching_candidate,
    profile_only_evidence_candidate,
    roadmap_candidate,
    semantic_matching_candidate,
    stale_candidate,
    trusted_skill_candidate,
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


def test_extracts_profile_evidence_at_lower_trust_than_career_evidence() -> None:
    profile_only = extract_features(profile_only_evidence_candidate(), reference_date=date(2026, 6, 17))
    career_backed = extract_features(semantic_matching_candidate(), reference_date=date(2026, 6, 17))

    assert profile_only.profile_retrieval_evidence >= 3
    assert profile_only.profile_ranking_evidence >= 2
    assert profile_only.profile_evaluation_evidence >= 1
    assert profile_only.retrieval_evidence == 0
    assert profile_only.profile_evidence_score > 0
    assert profile_only.profile_evidence_score < career_backed.career_evidence_score


def test_short_metric_phrases_use_word_boundaries() -> None:
    features = extract_features(roadmap_candidate(), reference_date=date(2026, 6, 17))

    assert "map" not in features.evidence_phrases
    assert features.evaluation_evidence == 0


def test_expanded_senior_ai_titles_score_as_strong_role_fit() -> None:
    for title in [
        "Founding AI Engineer",
        "Founding Machine Learning Engineer",
        "Staff AI Engineer",
        "Principal AI Engineer",
        "Relevance Engineer",
        "Search Relevance Engineer",
        "Ranking Engineer",
        "Recommendation Engineer",
        "ML Platform Engineer",
        "Applied AI Engineer",
        "Machine Learning Scientist",
    ]:
        candidate = semantic_matching_candidate()
        candidate["profile"]["current_title"] = title

        features = extract_features(candidate, reference_date=date(2026, 6, 17))

        assert features.role_score >= 5.5, title


def test_skill_trust_rewards_duration_assessments_and_career_support() -> None:
    trusted = extract_features(trusted_skill_candidate(), reference_date=date(2026, 6, 17))
    generic = extract_features(generic_ai_keyword_candidate(), reference_date=date(2026, 6, 17))

    assert trusted.skill_trust_score > trusted.relevant_skill_count
    assert trusted.skill_trust_score > generic.skill_trust_score + 6


def test_negated_retrieval_claims_do_not_count_as_positive_evidence() -> None:
    candidate = base_candidate()
    candidate["career_history"] = [
        {
            "company": "Acme",
            "title": "Software Engineer",
            "duration_months": 72,
            "is_current": True,
            "industry": "Software",
            "description": (
                "Built internal APIs. No production retrieval, ranking, semantic search, "
                "or evaluation ownership."
            ),
        }
    ]

    features = extract_features(candidate, reference_date=date(2026, 6, 17))

    assert features.retrieval_evidence == 0
    assert features.ranking_evidence == 0
    assert features.evaluation_evidence == 0
    assert features.retrieval_quality_score == 0


def test_skill_aliases_are_normalized_and_deduplicated() -> None:
    candidate = base_candidate()
    candidate["skills"] = [
        {"name": "vector-search", "proficiency": "advanced", "duration_months": 24},
        {"name": "Vector Search", "proficiency": "advanced", "duration_months": 24},
        {"name": "learning-to-rank", "proficiency": "advanced", "duration_months": 24},
        {"name": "cross-encoder", "proficiency": "advanced", "duration_months": 24},
    ]

    features = extract_features(candidate, reference_date=date(2026, 6, 17))

    assert features.relevant_skills == ("Cross Encoder", "Learning to Rank", "Vector Search")
    assert features.relevant_skill_count == 3


def test_missing_behavior_fields_are_unknown_not_negative() -> None:
    candidate = base_candidate()
    candidate["redrob_signals"] = {}

    features = extract_features(candidate, reference_date=date(2026, 6, 17))

    assert "not marked open to work" not in features.risk_flags
    assert "low recruiter response" not in features.risk_flags
    assert "long notice period" not in features.risk_flags


def test_current_production_evidence_is_weighted_above_old_exposure() -> None:
    current = base_candidate()
    old = base_candidate()
    old["career_history"] = list(reversed(old["career_history"]))
    old["career_history"][0]["is_current"] = True
    old["career_history"][1]["is_current"] = False

    current_features = extract_features(current, reference_date=date(2026, 6, 17))
    old_features = extract_features(old, reference_date=date(2026, 6, 17))

    assert current_features.evidence_confidence > old_features.evidence_confidence
