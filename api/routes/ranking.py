from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

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


@router.get("/rank/latest")
def latest_ranking() -> dict:
    return service.latest_payload()


@router.post("/rank/upload")
async def rank_uploaded_candidates(
    candidates_file: UploadFile = File(...),
    job_text: str | None = Form(default=None),
    job_file: UploadFile | None = File(default=None),
    top_n: int = Form(default=50),
) -> dict:
    try:
        return service.rank_uploaded_candidates(
            candidates_filename=candidates_file.filename or "",
            candidates_content=await candidates_file.read(),
            job_text=job_text,
            job_filename=job_file.filename if job_file else None,
            job_content=await job_file.read() if job_file else None,
            top_n=top_n,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

