from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import RankRequest
from api.services.ranker_service import RankerService


router = APIRouter(tags=["ranking"])
service = RankerService()


@router.post("/rank")
def rank_candidates(request: RankRequest) -> dict:
    try:
        return service.rank(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

