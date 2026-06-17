from __future__ import annotations

import re
from datetime import date

from redrob_ranker.reasoning import generate_reasoning
from redrob_ranker.scoring import rank_candidates, score_candidate
from tests.fixtures import base_candidate, keyword_stuffed_candidate, stale_candidate


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
