from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app
from api.services.gemini_service import PROTECTED_ATTRIBUTE_GUARDRAILS, GeminiService
from redrob_ranker.ai_fusion import detect_hidden_gem


def test_project_works_without_gemini_api_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_ENABLED", "true")
    client = TestClient(app)

    response = client.get("/api/rank/latest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_jd_insight"]["fallback_used"] is True
    assert payload["ai_jd_insight"]["gemini_enabled"] is False
    assert "ai_contextual_fit" in payload["rankings"][0]


def test_gemini_disabled_fallback_works(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_ENABLED", "false")
    monkeypatch.setenv("GEMINI_API_KEY", "not-used")
    service = GeminiService()

    result = service.generate_ai_jd_insight("Senior AI Engineer", {"role_title": "Senior AI Engineer"})

    assert result["fallback_used"] is True
    assert result["gemini_enabled"] is False
    assert result["role_archetype"] == "Senior AI Engineer"


def test_invalid_gemini_json_falls_back(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_ENABLED", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    service = GeminiService()
    monkeypatch.setattr(service, "_call_gemini", lambda prompt: "not-json")

    result = service.generate_contextual_fit({"fit_score": 80, "proof_score": 80, "risk_score": 0}, {}, {}, [])

    assert result["fallback_used"] is True
    assert result["gemini_enabled"] is False


def test_contextual_fit_score_is_clamped(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_ENABLED", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    service = GeminiService()
    monkeypatch.setattr(
        service,
        "_call_gemini",
        lambda prompt: '{"contextual_fit_score": 999, "semantic_fit_reason": "Evidence supported", "hidden_strengths": [], "weak_context_signals": [], "evidence_supported": [], "evidence_missing": [], "risk_notes": [], "recommended_interview_checks": []}',
    )

    result = service.generate_contextual_fit({"fit_score": 10, "proof_score": 10, "risk_score": 0}, {}, {}, [])

    assert result["fallback_used"] is False
    assert result["contextual_fit_score"] == 100


def test_gemini_output_never_changes_final_score(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_ENABLED", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    service = GeminiService()
    monkeypatch.setattr(
        service,
        "_call_gemini",
        lambda prompt: '{"contextual_fit_score": 99, "semantic_fit_reason": "Strong", "hidden_strengths": [], "weak_context_signals": [], "evidence_supported": [], "evidence_missing": [], "risk_notes": [], "recommended_interview_checks": []}',
    )
    payload = {
        "role_requirements": {},
        "rankings": [
            {
                "candidate_id": "A",
                "final_score": 42,
                "fit_score": 10,
                "proof_score": 10,
                "risk_score": 0,
                "hireability_score": 50,
                "evidence_ledger": {"positive_evidence": [], "missing_evidence": []},
                "risks": [],
                "missing_evidence": [],
                "interview_focus": [],
                "components": {},
            }
        ],
    }

    enriched = service.enrich_payload(payload)

    assert enriched["rankings"][0]["final_score"] == 42
    assert enriched["rankings"][0]["ai_contextual_fit"]["contextual_fit_score"] == 99


def test_hidden_gem_requires_proof_and_low_risk() -> None:
    rows = [
        {"candidate_id": "TOP", "fit_score": 95, "proof_score": 40, "risk_score": 0, "evidence_ledger": {"positive_evidence": []}},
        {
            "candidate_id": "GEM",
            "fit_score": 70,
            "proof_score": 85,
            "risk_score": 10,
            "evidence_ledger": {
                "positive_evidence": [
                    {"claim_or_proof": "strong_proof", "snippet": "Shipped ranking system", "concept": "ranking"}
                ]
            },
        },
        {
            "candidate_id": "RISKY",
            "fit_score": 65,
            "proof_score": 90,
            "risk_score": 70,
            "evidence_ledger": {
                "positive_evidence": [
                    {"claim_or_proof": "strong_proof", "snippet": "Shipped ranking system", "concept": "ranking"}
                ]
            },
        },
    ]

    assert detect_hidden_gem(rows[1], rows, {"contextual_fit_score": 90})["hidden_gem_candidate"] is True
    assert detect_hidden_gem(rows[2], rows, {"contextual_fit_score": 90})["hidden_gem_candidate"] is False
    assert detect_hidden_gem({**rows[1], "evidence_ledger": {"positive_evidence": []}}, rows, {"contextual_fit_score": 90})["hidden_gem_candidate"] is False


def test_recruiter_explanation_preserves_missing_evidence(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_ENABLED", "false")
    service = GeminiService()

    result = service.generate_recruiter_explanation(
        {"main_reason": "", "missing_evidence": []},
        {},
        {"positive_evidence": [], "missing_evidence": []},
        [],
        {},
    )

    assert "Missing from supplied data" in result["missing_proof"]


def test_prompt_guardrails_include_protected_attributes() -> None:
    lowered = PROTECTED_ATTRIBUTE_GUARDRAILS.lower()
    for term in ["gender", "age", "caste", "religion", "race", "disability", "protected trait"]:
        assert term in lowered


def test_all_new_ai_api_endpoints_return_metadata(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_ENABLED", "false")
    client = TestClient(app)
    row = client.get("/api/rank/latest").json()["rankings"][0]

    responses = [
        client.post("/api/ai/jd-insight", json={"job_text": "Senior AI Engineer"}),
        client.post(
            "/api/ai/contextual-fit",
            json={
                "candidate_payload": row,
                "job_matrix": {},
                "evidence_ledger": row["evidence_ledger"],
                "risk_radar": row["risks"],
            },
        ),
        client.post(
            "/api/ai/recruiter-explanation",
            json={
                "candidate_payload": row,
                "score_breakdown": row["components"],
                "evidence_ledger": row["evidence_ledger"],
                "risk_radar": row["risks"],
                "ai_contextual_fit": row["ai_contextual_fit"],
            },
        ),
        client.post("/api/ai/hidden-gems"),
        client.post("/api/ai/signal-fusion-summary"),
    ]

    for response in responses:
        assert response.status_code == 200
        payload = response.json()
        assert {"gemini_enabled", "model_used", "fallback_used", "generated_at"}.issubset(payload)
