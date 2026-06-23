from __future__ import annotations

import json
from datetime import date

from redrob_ranker.evidence_ledger import build_evidence_ledger
from redrob_ranker.fairness import strip_protected_attributes, uses_role_relevant_evidence_only
from redrob_ranker.io import build_product_ranking_output, write_product_outputs
from redrob_ranker.job_understanding import default_role_requirements
from redrob_ranker.reasoning import generate_structured_reasoning
from redrob_ranker.risk import build_risk_radar
from redrob_ranker.scoring import rank_scored_candidates, score_candidate, score_candidates
from tests.fixtures import (
    base_candidate,
    generic_ai_keyword_candidate,
    keyword_stuffed_candidate,
    profile_only_evidence_candidate,
)


def test_scored_candidate_exposes_normalized_product_scores() -> None:
    scored = score_candidate(base_candidate(), reference_date=date(2026, 6, 17))

    product = scored.product_scores

    assert 0 <= product.final_score <= 100
    assert 0 <= product.fit_score <= 100
    assert 0 <= product.proof_score <= 100
    assert 0 <= product.confidence_score <= 100
    assert 0 <= product.hireability_score <= 100
    assert 0 <= product.risk_score <= 100
    assert product.final_score > product.risk_score


def test_jd_aware_scoring_rewards_job_specific_must_have_skills() -> None:
    matrix = default_role_requirements()
    matrix.must_have_skills = ["Python", "FastAPI", "Vector Search"]
    matrix.domain_expectations = "candidate matching and retrieval"
    good = score_candidate(base_candidate("CAND_GOOD"), reference_date=date(2026, 6, 17), role_requirements=matrix)
    weak = score_candidate(keyword_stuffed_candidate("CAND_WEAK"), reference_date=date(2026, 6, 17), role_requirements=matrix)

    assert good.product_scores.fit_score > weak.product_scores.fit_score
    assert good.score > weak.score


def test_evidence_ledger_separates_claims_from_proof() -> None:
    scored = score_candidate(base_candidate(), reference_date=date(2026, 6, 17))
    ledger = build_evidence_ledger(scored, rank=1)

    claim_types = {item["claim_or_proof"] for item in ledger["positive_evidence"]}

    assert "claim" in claim_types
    assert "proof" in claim_types or "strong_proof" in claim_types
    assert ledger["source_fields"]
    assert ledger["score_impacts"]


def test_profile_only_evidence_is_labeled_as_claim_not_proof() -> None:
    scored = score_candidate(profile_only_evidence_candidate(), reference_date=date(2026, 6, 17))
    ledger = build_evidence_ledger(scored, rank=4)

    profile_items = [
        item for item in ledger["positive_evidence"] if item["source_field"].startswith("profile.")
    ]

    assert profile_items
    assert {item["claim_or_proof"] for item in profile_items} == {"claim"}


def test_structured_risk_radar_maps_existing_flags_to_risk_items() -> None:
    scored = score_candidate(generic_ai_keyword_candidate(), reference_date=date(2026, 6, 17))

    risks = build_risk_radar(scored)

    assert any(item["risk_type"] == "weak proof behind strong claims" for item in risks)
    assert all({"risk_type", "severity", "evidence", "score_impact", "explanation"} <= set(item) for item in risks)


def test_structured_reasoning_contains_recruiter_sections() -> None:
    scored = score_candidate(base_candidate(), reference_date=date(2026, 6, 17))
    ledger = build_evidence_ledger(scored, rank=1)

    reasoning = generate_structured_reasoning(scored, ledger)

    assert reasoning["why_shortlisted"]
    assert reasoning["best_evidence"]
    assert reasoning["main_concern"]
    assert reasoning["why_not_ranked_higher"]
    assert reasoning["interview_focus"]
    assert reasoning["hiring_feasibility_summary"]
    assert reasoning["risk_summary"]


def test_fairness_guard_strips_protected_attributes_without_removing_role_evidence() -> None:
    candidate = base_candidate()
    candidate["profile"].update({"gender": "female", "religion": "private", "age": 29})

    cleaned, ignored = strip_protected_attributes(candidate)

    assert uses_role_relevant_evidence_only() is True
    assert "gender" in ignored
    assert "religion" in ignored
    assert "age" in ignored
    assert "gender" not in cleaned["profile"]
    assert cleaned["profile"]["current_title"] == candidate["profile"]["current_title"]


def test_product_json_output_contains_metadata_role_requirements_and_ledgers(tmp_path) -> None:
    matrix = default_role_requirements()
    scored = score_candidates([base_candidate("CAND_1"), keyword_stuffed_candidate("CAND_2")], reference_date=date(2026, 6, 17))
    ranked = rank_scored_candidates(scored, top_n=2)

    payload = build_product_ranking_output(
        scored,
        ranked,
        role_requirements=matrix,
        top_n=2,
        runtime_seconds=1.23,
        job_supplied=True,
    )

    assert payload["metadata"]["project"] == "EvidenceGraph Ranker"
    assert payload["metadata"]["ranking_uses_role_relevant_evidence_only"] is True
    assert payload["role_requirements"]["role_title"] == "Senior AI Engineer"
    assert payload["rankings"][0]["evidence_ledger"]["candidate_id"] == "CAND_1"
    assert {"final_score", "fit_score", "proof_score", "confidence_score", "hireability_score", "risk_score"} <= set(payload["rankings"][0])

    write_product_outputs(payload, tmp_path, csv_filename="ranked.csv")
    assert (tmp_path / "ranked_candidates.json").exists()
    assert (tmp_path / "ranked.csv").exists()
    assert (tmp_path / "evidence_ledgers.json").exists()
    written = json.loads((tmp_path / "ranked_candidates.json").read_text(encoding="utf-8"))
    assert written["metadata"]["candidate_count"] == 2

