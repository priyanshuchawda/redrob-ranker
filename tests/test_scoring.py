from __future__ import annotations

import re
from datetime import date

from redrob_ranker.reasoning import generate_reasoning
from redrob_ranker.scoring import rank_candidates, score_candidate
from tests.fixtures import (
    base_candidate,
    cv_speech_candidate,
    generic_ai_keyword_candidate,
    keyword_stuffed_candidate,
    not_open_candidate,
    outside_india_candidate,
    plain_language_matching_candidate,
    profile_only_evidence_candidate,
    semantic_matching_candidate,
    stale_candidate,
    trusted_skill_candidate,
)


def test_true_retrieval_candidate_outranks_keyword_stuffed_profile() -> None:
    good = score_candidate(base_candidate(), reference_date=date(2026, 6, 17))
    stuffed = score_candidate(keyword_stuffed_candidate(), reference_date=date(2026, 6, 17))

    assert good.score > stuffed.score + 20
    assert good.features.keyword_stuffing_risk is False
    assert stuffed.features.keyword_stuffing_risk is True


def test_availability_penalty_lowers_otherwise_strong_candidate() -> None:
    active = score_candidate(base_candidate("CAND_0000001"), reference_date=date(2026, 6, 17))
    stale = score_candidate(stale_candidate("CAND_0000003"), reference_date=date(2026, 6, 17))

    assert active.score > stale.score
    assert active.score - stale.score >= 10


def test_ranking_is_score_descending_then_candidate_id_ascending() -> None:
    first = base_candidate("CAND_0000002")
    second = base_candidate("CAND_0000001")

    ranked = rank_candidates([first, second], reference_date=date(2026, 6, 17), top_n=2)

    assert [row.candidate_id for row in ranked] == ["CAND_0000001", "CAND_0000002"]
    assert [row.rank for row in ranked] == [1, 2]


def test_reasoning_is_grounded_and_mentions_concerns() -> None:
    scored = score_candidate(stale_candidate(), reference_date=date(2026, 6, 17))
    reasoning = generate_reasoning(scored)

    assert "Applied ML Engineer" in reasoning
    assert "7.0 yrs" in reasoning
    assert "hybrid search" in reasoning or "recommendation ranking" in reasoning
    assert "response rate 0.05" in reasoning
    assert "concern" in reasoning.lower()


def test_reasoning_deduplicates_embedding_phrases() -> None:
    candidate = base_candidate()
    candidate["career_history"][0]["description"] = (
        "Shipped semantic search using embedding features, embeddings refreshes, "
        "and recruiter-facing ranking."
    )
    candidate["career_history"][1]["description"] = "Built Python ML services."

    scored = score_candidate(candidate, reference_date=date(2026, 6, 17))
    reasoning = generate_reasoning(scored)

    assert not (re.search(r"\bembedding\b", reasoning) and re.search(r"\bembeddings\b", reasoning))


def test_plain_language_matching_candidate_beats_tool_keyword_profile() -> None:
    plain_language = score_candidate(plain_language_matching_candidate(), reference_date=date(2026, 6, 17))
    keyword_profile = score_candidate(keyword_stuffed_candidate(), reference_date=date(2026, 6, 17))

    assert plain_language.score > keyword_profile.score + 35


def test_outside_india_and_not_open_profiles_are_downweighted() -> None:
    local = score_candidate(base_candidate("CAND_0000001"), reference_date=date(2026, 6, 17))
    outside = score_candidate(outside_india_candidate("CAND_0000005"), reference_date=date(2026, 6, 17))
    not_open = score_candidate(not_open_candidate("CAND_0000006"), reference_date=date(2026, 6, 17))

    assert local.score > outside.score + 18
    assert local.score > not_open.score + 6


def test_cv_speech_heavy_ai_profile_loses_to_retrieval_production_profile() -> None:
    retrieval = score_candidate(base_candidate("CAND_0000001"), reference_date=date(2026, 6, 17))
    cv_speech = score_candidate(cv_speech_candidate("CAND_0000007"), reference_date=date(2026, 6, 17))

    assert retrieval.score > cv_speech.score + 25
    assert "non-target ML domain" in cv_speech.features.risk_flags


def test_reasoning_mentions_not_open_concern() -> None:
    scored = score_candidate(not_open_candidate(), reference_date=date(2026, 6, 17))
    reasoning = generate_reasoning(scored)

    assert "not marked open to work" in reasoning


def test_reasoning_uses_readable_plain_language_evidence_labels() -> None:
    candidate = plain_language_matching_candidate()
    candidate["career_history"][0]["description"] = (
        "Owned search and discovery systems that surface relevant results for "
        "each user intent."
    )
    candidate["career_history"][1]["description"] = "Built product ML systems."

    reasoning = generate_reasoning(score_candidate(candidate, reference_date=date(2026, 6, 17)))

    assert "surface" not in reasoning
    assert "relevance systems" in reasoning


def test_score_candidate_exposes_component_breakdown() -> None:
    scored = score_candidate(base_candidate(), reference_date=date(2026, 6, 17))

    assert scored.components.role > 0
    assert scored.components.retrieval > 0
    assert scored.components.ranking > 0
    assert scored.components.evaluation > 0
    assert scored.components.risk == 0
    assert scored.components.total == scored.score


def test_semantic_matching_candidate_beats_generic_ai_profile() -> None:
    semantic = score_candidate(semantic_matching_candidate(), reference_date=date(2026, 6, 17))
    generic_ai = score_candidate(generic_ai_keyword_candidate(), reference_date=date(2026, 6, 17))

    assert semantic.score > generic_ai.score + 45
    assert "generic AI without shipped retrieval evidence" in generic_ai.features.risk_flags


def test_career_backed_evidence_scores_above_profile_only_claims() -> None:
    career_backed = score_candidate(semantic_matching_candidate(), reference_date=date(2026, 6, 17))
    profile_only = score_candidate(profile_only_evidence_candidate(), reference_date=date(2026, 6, 17))

    assert profile_only.components.profile_evidence > 0
    assert career_backed.score > profile_only.score + 8


def test_skill_component_uses_trust_score_not_raw_count_only() -> None:
    trusted = score_candidate(trusted_skill_candidate(), reference_date=date(2026, 6, 17))
    generic = score_candidate(generic_ai_keyword_candidate(), reference_date=date(2026, 6, 17))

    assert trusted.components.skills > generic.components.skills
