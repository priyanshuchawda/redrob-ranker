from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import CompareRequest
from api.routes.ranking import service


router = APIRouter(tags=["compare"])


@router.post("/compare")
def compare_candidates(request: CompareRequest) -> dict:
    try:
        return service.compare(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

