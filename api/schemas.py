from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RankRequest(BaseModel):
    job_text: str | None = None
    candidates: list[dict[str, Any]] | None = None
    top_n: int = Field(default=50, ge=1)


class CompareRequest(BaseModel):
    job_text: str | None = None
    candidates: list[dict[str, Any]] | None = None
    candidate_a_id: str
    candidate_b_id: str


class EvaluateRequest(BaseModel):
    ranking: dict[str, Any] | None = None
    labels: dict[str, int] | None = None
    top_n: int = Field(default=10, ge=1)

