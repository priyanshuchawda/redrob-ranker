from __future__ import annotations

from redrob_ranker.job_understanding import default_role_requirements, parse_job_description


def test_parse_job_description_extracts_role_requirement_matrix() -> None:
    job_text = """
    Senior AI Engineer
    Must have: Python, FastAPI, vector search, evaluation.
    Strong signals: shipped retrieval systems, ranking, production APIs.
    Good to have: Kubernetes, recommender systems.
    5-9 years experience. Location: Pune or Bangalore, India. Notice under 45 days.
    Leadership: mentor engineers and own architecture. Risk blockers: no production ownership.
    """

    matrix = parse_job_description(job_text)

    assert matrix.role_title == "Senior AI Engineer"
    assert "Python" in matrix.must_have_skills
    assert "FastAPI" in matrix.must_have_skills
    assert "vector search" in matrix.must_have_skills
    assert "shipped retrieval systems" in matrix.strong_signal_skills
    assert "Kubernetes" in matrix.good_to_have_skills
    assert matrix.seniority_expectations == "5-9 years experience"
    assert "production" in matrix.production_expectations.lower()
    assert "Pune" in matrix.location_requirements
    assert "notice under 45 days" in matrix.availability_requirements.lower()
    assert "no production ownership" in matrix.risk_blockers
    assert matrix.raw_job_text == job_text.strip()


def test_default_role_requirements_preserve_challenge_calibration() -> None:
    matrix = default_role_requirements()

    assert matrix.role_title == "Senior AI Engineer"
    assert "Python" in matrix.must_have_skills
    assert "retrieval" in " ".join(matrix.strong_signal_skills).lower()
    assert "ranking" in " ".join(matrix.strong_signal_skills).lower()
    assert matrix.raw_job_text

