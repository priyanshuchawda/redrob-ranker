from __future__ import annotations

from scripts.synthetic_evaluation import evaluate, generate_cases


def test_synthetic_archetypes_separate_shortlist_from_adversarial_profiles() -> None:
    cases = generate_cases(per_archetype=2, seed=20260617)
    metrics, details = evaluate(cases, top_n=6)

    assert metrics["precision_at_n"] == 1.0
    assert metrics["recall_at_n"] == 1.0
    assert metrics["ndcg_at_n"] >= 0.96
    assert {row["archetype"] for row in details[:6]} == {
        "strong_search",
        "plain_language_fit",
        "missing_telemetry_fit",
    }
    assert all(row["archetype"] != "negated_claims" for row in details[:6])
    assert all(row["archetype"] != "keyword_stuffer" for row in details[:6])
