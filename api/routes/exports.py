from __future__ import annotations

from fastapi import APIRouter, Response

from api.routes.ranking import service


router = APIRouter(tags=["exports"])


@router.get("/exports/ranked-json")
def ranked_json() -> dict:
    return service.latest_payload()


@router.get("/exports/ranked-csv")
def ranked_csv() -> Response:
    csv_text = service.latest_csv()
    return Response(content=csv_text, media_type="text/csv")

