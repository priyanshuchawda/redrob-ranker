from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def test_api_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rank_upload_accepts_job_text_and_jsonl_candidates() -> None:
    client = TestClient(app)
    candidate = (
        '{"candidate_id":"UPLOAD_001","profile":{"headline":"Senior AI Engineer",'
        '"location":"Bangalore, India","years_of_experience":7},'
        '"skills":[{"name":"Python"},{"name":"FastAPI"}],'
        '"career_history":[{"title":"Senior AI Engineer",'
        '"description":"Shipped a production ranking API using Python and FastAPI."}]}'
    )

    response = client.post(
        "/api/rank/upload",
        data={
            "job_text": "Senior AI Engineer. Must have Python and FastAPI.",
            "top_n": "10",
        },
        files={"candidates_file": ("candidates.jsonl", candidate, "application/jsonl")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["candidate_count"] == 1
    assert payload["metadata"]["job_supplied"] is True
    assert payload["rankings"][0]["candidate_id"] == "UPLOAD_001"


def test_rank_upload_reports_malformed_candidate_file() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/rank/upload",
        files={"candidates_file": ("candidates.jsonl", "{not-json}", "application/jsonl")},
    )

    assert response.status_code == 400
    assert "candidate" in response.json()["detail"].lower()


def test_latest_ranking_and_comparison_reuse_uploaded_candidates() -> None:
    client = TestClient(app)
    candidates = [
        {
            "candidate_id": "LIVE_A",
            "profile": {
                "headline": "Senior AI Engineer",
                "years_of_experience": 7,
                "location": "Bangalore, India",
            },
            "career_history": [
                {
                    "title": "Senior AI Engineer",
                    "description": "Shipped production semantic search and ranking evaluation.",
                }
            ],
            "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        },
        {
            "candidate_id": "LIVE_B",
            "profile": {
                "headline": "ML Engineer",
                "years_of_experience": 5,
                "location": "Pune, India",
            },
            "career_history": [
                {
                    "title": "ML Engineer",
                    "description": "Built Python model serving and data pipelines.",
                }
            ],
            "skills": [{"name": "Python"}],
        },
    ]
    rank_response = client.post(
        "/api/rank",
        json={
            "job_text": "Senior AI Engineer. Must have Python, ranking, and evaluation.",
            "candidates": candidates,
            "top_n": 2,
        },
    )
    assert rank_response.status_code == 200

    latest_response = client.get("/api/rank/latest")
    comparison_response = client.post(
        "/api/compare",
        json={"candidate_a_id": "LIVE_A", "candidate_b_id": "LIVE_B"},
    )

    assert latest_response.status_code == 200
    assert {
        row["candidate_id"] for row in latest_response.json()["rankings"]
    } == {"LIVE_A", "LIVE_B"}
    assert comparison_response.status_code == 200
    assert comparison_response.json()["candidate_a"]["candidate_id"] == "LIVE_A"

