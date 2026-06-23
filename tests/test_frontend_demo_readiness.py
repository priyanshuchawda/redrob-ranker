from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_comparison_page_uses_backend_comparison_api() -> None:
    source = (ROOT / "frontend" / "app" / "compare" / "page.tsx").read_text(
        encoding="utf-8"
    )

    assert "compareCandidates(" in source
    assert "score_component_differences" in source
    assert "evidence_differences" in source
    assert "what_to_verify" in source


def test_frontend_loads_latest_backend_ranking() -> None:
    source = (ROOT / "frontend" / "lib" / "api.ts").read_text(encoding="utf-8")

    assert "/api/rank/latest" in source


def test_run_ranking_page_exposes_live_failure_and_upload_api() -> None:
    source = (
        ROOT / "frontend" / "app" / "run-ranking" / "page.tsx"
    ).read_text(encoding="utf-8")

    assert "rankUploadedCandidates(" in source
    assert "Live ranking failed. Showing demo fallback." in source
