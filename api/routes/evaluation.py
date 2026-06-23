from __future__ import annotations

from fastapi import APIRouter

from api.schemas import EvaluateRequest
from api.routes.ranking import service


router = APIRouter(tags=["evaluation"])


@router.post("/evaluate")
def evaluate(request: EvaluateRequest) -> dict:
    return service.evaluate(request)

