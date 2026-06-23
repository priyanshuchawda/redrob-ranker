from __future__ import annotations

from datetime import date

from redrob_ranker.battlecards import render_battlecards
from redrob_ranker.comparison import compare_scored_candidates
from redrob_ranker.io import build_product_ranking_output
from redrob_ranker.job_understanding import default_role_requirements
from redrob_ranker.scoring import rank_scored_candidates, score_candidates
from tests.fixtures import base_candidate, keyword_stuffed_candidate


def test_battlecards_render_recruiter_friendly_sections() -> None:
    scored = score_candidates([base_candidate("CAND_A"), keyword_stuffed_candidate("CAND_B")], reference_date=date(2026, 6, 17))
    ranked = rank_scored_candidates(scored, top_n=2)
    payload = build_product_ranking_output(scored, ranked, role_requirements=default_role_requirements(), top_n=2, runtime_seconds=0.5, job_supplied=False)

    markdown = render_battlecards(payload, top_n=2)

    assert "Candidate CAND_A" in markdown
    assert "Why shortlisted" in markdown
    assert "Best evidence" in markdown
    assert "Interview focus" in markdown
    assert "Risk summary" in markdown


def test_comparison_explains_score_and_evidence_differences() -> None:
    scored = score_candidates([base_candidate("CAND_A"), keyword_stuffed_candidate("CAND_B")], reference_date=date(2026, 6, 17))
    by_id = {row.candidate_id: row for row in scored}

    comparison = compare_scored_candidates(by_id["CAND_A"], by_id["CAND_B"], role_requirements=default_role_requirements())

    assert comparison["candidate_a"]["candidate_id"] == "CAND_A"
    assert comparison["candidate_b"]["candidate_id"] == "CAND_B"
    assert "ranks above" in comparison["why_a_ranks_above_b"]
    assert comparison["score_component_differences"]
    assert comparison["evidence_differences"]
    assert comparison["risks_for_a"] == []
    assert comparison["what_to_verify"]

