from __future__ import annotations

import json

from fastapi.testclient import TestClient

from api.main import app
from scripts.benchmark_runtime import duplicate_candidates, run_benchmark
from redrob_ranker.io import build_product_ranking_output
from redrob_ranker.job_understanding import default_role_requirements
from redrob_ranker.review_tags import generate_review_tags
from redrob_ranker.scoring import rank_scored_candidates, score_candidate, score_candidates
from redrob_ranker.trust_audit import build_trust_audit
from tests.fixtures import base_candidate, generic_ai_keyword_candidate, outside_india_candidate


def _payload() -> dict:
    scored = score_candidates([base_candidate("CAND_A"), generic_ai_keyword_candidate("CAND_B")])
    ranked = rank_scored_candidates(scored, top_n=2)
    return build_product_ranking_output(
        scored,
        ranked,
        role_requirements=default_role_requirements(),
        top_n=2,
        runtime_seconds=0.01,
        job_supplied=True,
    )


def test_review_tags_surface_no_major_blocker_for_strong_candidate() -> None:
    scored = score_candidate(base_candidate("CAND_STRONG"))
    tags = generate_review_tags(scored, {"missing_evidence": []})
    assert tags == ["No major blocker"]


def test_review_tags_surface_location_and_weak_proof_risks() -> None:
    outside = score_candidate(outside_india_candidate("CAND_OUTSIDE"))
    generic = score_candidate(generic_ai_keyword_candidate("CAND_GENERIC"))
    assert "Location risk" in generate_review_tags(outside, {"missing_evidence": []})
    assert "Strong claims but weak proof" in generate_review_tags(generic, {"missing_evidence": []})


def test_product_payload_contains_review_tags_and_role_requirements() -> None:
    payload = _payload()
    assert payload["role_requirements"]["role_title"]
    assert payload["rankings"][0]["review_tag"]
    assert payload["rankings"][0]["review_tags"]


def test_trust_audit_summary_counts_missing_and_risk_categories() -> None:
    audit = build_trust_audit(_payload())
    assert audit["total_candidates"] == 2
    assert "score_distribution" in audit
    assert "proof_vs_claim_summary" in audit
    assert audit["proxy_evaluation_warning"]


def test_trust_audit_api_route_returns_summary() -> None:
    client = TestClient(app)
    response = client.get("/api/trust-audit")
    assert response.status_code == 200
    assert response.json()["total_candidates"] >= 1


def test_benchmark_duplicate_candidates_makes_unique_ids() -> None:
    rows = duplicate_candidates([base_candidate("CAND_BASE")], 3)
    assert [row["candidate_id"] for row in rows] == ["BENCH_0000001", "BENCH_0000002", "BENCH_0000003"]


def test_benchmark_tiny_size_runs(tmp_path) -> None:
    path = tmp_path / "candidates.jsonl"
    path.write_text(json.dumps(base_candidate("CAND_ONE")) + "\n", encoding="utf-8")
    report = run_benchmark(path, None, [2], top_n=1)
    assert report["results"][0]["status"] == "completed"
    assert report["results"][0]["size"] == 2


def test_frontend_sources_include_jd_matrix_demo_mode_and_trust_audit() -> None:
    run_page = (app_root() / "frontend" / "app" / "run-ranking" / "page.tsx").read_text(encoding="utf-8")
    dashboard = (app_root() / "frontend" / "app" / "dashboard" / "page.tsx").read_text(encoding="utf-8")
    trust_page = (app_root() / "frontend" / "app" / "trust-audit" / "page.tsx").read_text(encoding="utf-8")
    table = (app_root() / "frontend" / "components" / "CandidateTable.tsx").read_text(encoding="utf-8")
    assert "Use Demo Scenario" in run_page
    assert "RoleRequirementMatrix" in dashboard
    assert "TrustAuditSummary" in trust_page
    assert "Review Tag" in table


def app_root():
    from pathlib import Path

    return Path(__file__).resolve().parents[1]
