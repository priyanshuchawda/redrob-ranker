from __future__ import annotations

from fastapi import APIRouter

from api.routes.ranking import service

router = APIRouter(tags=["trust-audit"])


@router.get("/trust-audit")
def trust_audit() -> dict:
    return service.trust_audit()
