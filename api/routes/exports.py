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
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="ranked_candidates.csv"'},
    )


@router.get("/exports/submission-csv")
def submission_csv() -> Response:
    csv_text = service.latest_submission_csv()
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="redrob_submission.csv"'},
    )


@router.get("/exports/submission-xlsx")
def submission_xlsx() -> Response:
    return Response(
        content=service.latest_submission_xlsx(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="redrob_ranked_output.xlsx"'},
    )

