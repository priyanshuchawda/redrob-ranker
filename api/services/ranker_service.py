from __future__ import annotations

import csv
import io
import sys
import tempfile
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from api.schemas import CompareRequest, EvaluateRequest, RankRequest
from redrob_ranker.comparison import compare_scored_candidates
from redrob_ranker.evaluation import evaluate_payload
from redrob_ranker.io import build_product_ranking_output
from redrob_ranker.job_understanding import default_role_requirements, parse_job_description
from redrob_ranker.scoring import rank_scored_candidates, score_candidates
from redrob_ranker.schema import load_candidate_records
from redrob_ranker.trust_audit import build_trust_audit
from api.services.gemini_service import gemini_service


class RankerService:
    def __init__(self) -> None:
        self._latest_payload: dict[str, Any] | None = None
        self._latest_scored: dict[str, Any] = {}
        self._latest_role_requirements: RoleRequirementMatrix | None = None

    def get_demo_data(self) -> dict:
        return {"job_text": _demo_job_text(), "candidates": _demo_candidates()}

    def rank(self, request: RankRequest) -> dict:
        started = perf_counter()
        candidates = request.candidates or _load_demo_candidates()
        matrix = parse_job_description(request.job_text) if request.job_text else default_role_requirements()
        role_for_scoring = matrix if request.job_text else None
        scored = score_candidates(candidates, reference_date=date(2026, 6, 17), role_requirements=role_for_scoring)
        ranked = rank_scored_candidates(scored, top_n=min(request.top_n, len(scored)))
        payload = build_product_ranking_output(
            scored,
            ranked,
            role_requirements=matrix,
            top_n=min(request.top_n, len(scored)),
            runtime_seconds=perf_counter() - started,
            job_supplied=bool(request.job_text),
        )
        payload = gemini_service.enrich_payload(payload, job_text=request.job_text)
        self._latest_payload = payload
        self._latest_scored = {row.candidate_id: row for row in scored}
        self._latest_role_requirements = matrix
        return payload

    def rank_uploaded_candidates(
        self,
        *,
        candidates_filename: str,
        candidates_content: bytes,
        job_text: str | None,
        job_filename: str | None = None,
        job_content: bytes | None = None,
        top_n: int = 50,
    ) -> dict:
        if top_n < 1:
            raise ValueError("top_n must be at least 1")
        if not candidates_filename:
            raise ValueError("Candidate upload must include a filename")

        supplied_job_text = job_text
        if job_content is not None:
            try:
                supplied_job_text = job_content.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"Job file {job_filename or ''} must be UTF-8 text") from exc

        suffix = _upload_suffix(candidates_filename)
        with tempfile.TemporaryDirectory(prefix="evidencegraph-upload-") as temp_dir:
            candidate_path = Path(temp_dir) / f"candidates{suffix}"
            candidate_path.write_bytes(candidates_content)
            try:
                candidates = [
                    record.to_scoring_dict()
                    for record in load_candidate_records(candidate_path)
                ]
            except (OSError, ValueError) as exc:
                raise ValueError(f"Candidate upload could not be parsed: {exc}") from exc

        if not candidates:
            raise ValueError("Candidate upload did not contain any records")
        return self.rank(
            RankRequest(
                job_text=supplied_job_text,
                candidates=candidates,
                top_n=top_n,
            )
        )

    def list_candidates(self) -> dict:
        payload = self.latest_payload()
        return {"candidates": payload.get("rankings", [])}

    def get_candidate(self, candidate_id: str) -> dict | None:
        for row in self.latest_payload().get("rankings", []):
            if row.get("candidate_id") == candidate_id:
                return row
        return None

    def compare(self, request: CompareRequest) -> dict:
        if (
            request.candidates is None
            and request.job_text is None
            and request.candidate_a_id in self._latest_scored
            and request.candidate_b_id in self._latest_scored
        ):
            comparison = compare_scored_candidates(
                self._latest_scored[request.candidate_a_id],
                self._latest_scored[request.candidate_b_id],
                self._latest_role_requirements or default_role_requirements(),
            )
            return _add_ai_semantic_comparison(comparison, self.latest_payload())

        matrix = parse_job_description(request.job_text) if request.job_text else default_role_requirements()
        candidates = request.candidates or _load_demo_candidates()
        scored = score_candidates(
            candidates,
            reference_date=date(2026, 6, 17),
            role_requirements=matrix if request.job_text else None,
        )
        by_id = {row.candidate_id: row for row in scored}
        try:
            comparison = compare_scored_candidates(by_id[request.candidate_a_id], by_id[request.candidate_b_id], matrix)
            payload = build_product_ranking_output(
                scored,
                rank_scored_candidates(scored, top_n=len(scored)),
                role_requirements=matrix,
                top_n=len(scored),
                runtime_seconds=0,
                job_supplied=bool(request.job_text),
            )
            payload = gemini_service.enrich_payload(payload, job_text=request.job_text)
            return _add_ai_semantic_comparison(comparison, payload)
        except KeyError as exc:
            raise ValueError(f"Candidate id not found: {exc.args[0]}") from exc

    def evaluate(self, request: EvaluateRequest) -> dict:
        payload = request.ranking or self.latest_payload()
        return evaluate_payload(payload, labels=request.labels, top_n=request.top_n)

    def trust_audit(self) -> dict:
        audit = build_trust_audit(self.latest_payload())
        audit["ai_summary"] = gemini_service.trust_audit_ai_summary(audit)
        return audit

    def latest_payload(self) -> dict:
        if self._latest_payload is None:
            return self.rank(RankRequest(job_text=_demo_job_text(), candidates=_load_demo_candidates(), top_n=10))
        return self._latest_payload

    def latest_csv(self) -> str:
        payload = self.latest_payload()
        handle = io.StringIO()
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "candidate_id",
                "final_score",
                "fit_score",
                "proof_score",
                "confidence_score",
                "hireability_score",
                "risk_score",
                "main_reason",
            ],
        )
        writer.writeheader()
        for row in payload.get("rankings", []):
            writer.writerow({field: row.get(field, "") for field in writer.fieldnames})
        return handle.getvalue()


def _load_demo_candidates() -> list[dict]:
    path = ROOT / "data" / "candidates.jsonl"
    if path.exists():
        return [record.to_scoring_dict() for record in load_candidate_records(path)]
    return _demo_candidates()


def _demo_job_text() -> str:
    path = ROOT / "data" / "job.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return (
        "Senior AI Engineer\n"
        "Must have: Python, FastAPI, vector search, ranking, evaluation.\n"
        "Strong signals: shipped retrieval systems, candidate matching, production APIs.\n"
        "Good to have: Kubernetes, MLOps, recommendation systems.\n"
        "5-9 years experience. Location: Pune or Bangalore, India. Notice under 45 days."
    )


def _demo_candidates() -> list[dict]:
    return [
        {
            "candidate_id": "CAND_DEMO_001",
            "profile": {
                "anonymized_name": "Demo Candidate 1",
                "headline": "Senior AI Engineer for search relevance",
                "summary": "Builds retrieval and ranking systems for product teams.",
                "location": "Bangalore, India",
                "country": "India",
                "years_of_experience": 7.0,
                "current_title": "Senior AI Engineer",
                "current_company": "ProductAI",
                "current_industry": "AI/ML",
            },
            "career_history": [
                {
                    "company": "ProductAI",
                    "title": "Senior AI Engineer",
                    "duration_months": 42,
                    "is_current": True,
                    "industry": "AI/ML",
                    "description": "Owned and shipped production semantic search, two-tower candidate matching, cross encoder reranking, NDCG evaluation, and FastAPI serving.",
                }
            ],
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 72, "endorsements": 30},
                {"name": "FastAPI", "proficiency": "advanced", "duration_months": 36, "endorsements": 12},
                {"name": "Vector Search", "proficiency": "advanced", "duration_months": 36, "endorsements": 20},
            ],
            "redrob_signals": {
                "last_active_date": "2026-06-05",
                "open_to_work_flag": True,
                "recruiter_response_rate": 0.82,
                "notice_period_days": 30,
                "preferred_work_mode": "hybrid",
                "willing_to_relocate": True,
                "profile_completeness_score": 92,
            },
        },
        {
            "candidate_id": "CAND_DEMO_002",
            "profile": {
                "anonymized_name": "Demo Candidate 2",
                "headline": "ML Platform Engineer",
                "summary": "Strong backend and ML platform ownership.",
                "location": "Pune, India",
                "country": "India",
                "years_of_experience": 6.0,
                "current_title": "ML Platform Engineer",
                "current_company": "SaaSCo",
                "current_industry": "SaaS",
            },
            "career_history": [
                {
                    "company": "SaaSCo",
                    "title": "ML Platform Engineer",
                    "duration_months": 48,
                    "is_current": True,
                    "industry": "SaaS",
                    "description": "Built Python APIs, Kubernetes deployments, model serving, monitoring, and data pipelines for ML teams.",
                }
            ],
            "skills": [
                {"name": "Python", "proficiency": "expert", "duration_months": 60, "endorsements": 22},
                {"name": "Kubernetes", "proficiency": "advanced", "duration_months": 30, "endorsements": 10},
                {"name": "MLOps", "proficiency": "advanced", "duration_months": 32, "endorsements": 13},
            ],
            "redrob_signals": {
                "last_active_date": "2026-05-30",
                "open_to_work_flag": True,
                "recruiter_response_rate": 0.68,
                "notice_period_days": 45,
                "preferred_work_mode": "hybrid",
                "willing_to_relocate": True,
                "profile_completeness_score": 86,
            },
        },
    ]


def _upload_suffix(filename: str) -> str:
    lower_name = filename.lower()
    if lower_name.endswith(".jsonl.gz"):
        return ".jsonl.gz"
    suffix = Path(lower_name).suffix
    if suffix in {".jsonl", ".ndjson", ".json", ".csv"}:
        return suffix
    raise ValueError(
        "Unsupported candidate upload type. Use JSONL, JSONL.GZ, JSON, or CSV."
    )


def _add_ai_semantic_comparison(comparison: dict, payload: dict) -> dict:
    rows = {row.get("candidate_id"): row for row in payload.get("rankings", [])}
    a = rows.get((comparison.get("candidate_a") or {}).get("candidate_id"), {})
    b = rows.get((comparison.get("candidate_b") or {}).get("candidate_id"), {})
    comparison["ai_semantic_comparison"] = {
        **gemini_service.signal_fusion_summary(payload),
        "summary": "Gemini assisted insight compares contextual strengths separately from deterministic ranking.",
        "hidden_strengths_difference": list((a.get("ai_contextual_fit") or {}).get("hidden_strengths") or [])
        + list((b.get("ai_contextual_fit") or {}).get("hidden_strengths") or []),
        "risk_difference": [
            *(risk.get("explanation", "") for risk in a.get("risks", []) if isinstance(risk, dict)),
            *(risk.get("explanation", "") for risk in b.get("risks", []) if isinstance(risk, dict)),
        ],
        "interview_checks": list(comparison.get("what_to_verify") or []),
    }
    return comparison

