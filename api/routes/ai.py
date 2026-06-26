from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from api.routes.ranking import service as ranker_service
from api.services.gemini_service import gemini_service


router = APIRouter(tags=["ai"])


class JDInsightRequest(BaseModel):
    job_text: str | None = None
    deterministic_matrix: dict[str, Any] | None = None


class ContextualFitRequest(BaseModel):
    candidate_payload: dict[str, Any]
    job_matrix: dict[str, Any] | None = None
    evidence_ledger: dict[str, Any] | None = None
    risk_radar: list[dict[str, Any]] | None = None


class RecruiterExplanationRequest(BaseModel):
    candidate_payload: dict[str, Any]
    score_breakdown: dict[str, Any] | None = None
    evidence_ledger: dict[str, Any] | None = None
    risk_radar: list[dict[str, Any]] | None = None
    ai_contextual_fit: dict[str, Any] | None = None


@router.post("/ai/jd-insight")
def ai_jd_insight(request: JDInsightRequest) -> dict:
    matrix = request.deterministic_matrix or ranker_service.latest_payload().get("role_requirements") or {}
    return gemini_service.generate_ai_jd_insight(request.job_text, matrix)


@router.post("/ai/contextual-fit")
def ai_contextual_fit(request: ContextualFitRequest) -> dict:
    return gemini_service.generate_contextual_fit(
        request.candidate_payload,
        request.job_matrix,
        request.evidence_ledger,
        request.risk_radar,
    )


@router.post("/ai/recruiter-explanation")
def ai_recruiter_explanation(request: RecruiterExplanationRequest) -> dict:
    return gemini_service.generate_recruiter_explanation(
        request.candidate_payload,
        request.score_breakdown or {},
        request.evidence_ledger,
        request.risk_radar,
        request.ai_contextual_fit,
    )


@router.post("/ai/hidden-gems")
def ai_hidden_gems() -> dict:
    return gemini_service.hidden_gems(ranker_service.latest_payload())


@router.post("/ai/signal-fusion-summary")
def ai_signal_fusion_summary() -> dict:
    return gemini_service.signal_fusion_summary(ranker_service.latest_payload())
