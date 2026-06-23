from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.routes.ranking import service


router = APIRouter(tags=["candidates"])


@router.get("/candidates")
def list_candidates() -> dict:
    return service.list_candidates()


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str) -> dict:
    candidate = service.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail=f"Candidate not found: {candidate_id}")
    return candidate

