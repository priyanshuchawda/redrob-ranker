from __future__ import annotations

import csv
import gzip
import json

import pytest

from redrob_ranker.schema import adapt_candidate_record, load_candidate_records
from tests.fixtures import base_candidate


def test_load_candidate_records_reads_json_array_and_preserves_raw_record(tmp_path) -> None:
    path = tmp_path / "candidates.json"
    raw = base_candidate("CAND_JSON")
    path.write_text(json.dumps([raw]), encoding="utf-8")

    records = load_candidate_records(path, data_quality_report_path=tmp_path / "quality.json")

    assert len(records) == 1
    assert records[0].candidate_id == "CAND_JSON"
    assert records[0].raw_record == raw
    assert records[0].to_scoring_dict()["candidate_id"] == "CAND_JSON"
    report = json.loads((tmp_path / "quality.json").read_text(encoding="utf-8"))
    assert report["loaded_records"] == 1
    assert report["assumptions"]


def test_load_candidate_records_reads_csv_with_best_effort_mapping(tmp_path) -> None:
    path = tmp_path / "candidates.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "name", "title", "summary", "skills", "location", "availability"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "CAND_CSV",
                "name": "Asha Rao",
                "title": "Senior AI Engineer",
                "summary": "Shipped production vector search and ranking APIs.",
                "skills": "Python; FastAPI; Vector Search",
                "location": "Bangalore, India",
                "availability": "30 days",
            }
        )

    records = load_candidate_records(path)

    assert records[0].candidate_id == "CAND_CSV"
    assert records[0].name == "Asha Rao"
    assert "Python" in records[0].skills
    assert records[0].to_scoring_dict()["profile"]["current_title"] == "Senior AI Engineer"


@pytest.mark.parametrize("compressed", [False, True])
def test_load_candidate_records_reads_jsonl_and_gzip_jsonl(tmp_path, compressed: bool) -> None:
    path = tmp_path / ("candidates.jsonl.gz" if compressed else "candidates.jsonl")
    opener = gzip.open if compressed else open
    with opener(path, "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(base_candidate("CAND_JSONL")) + "\n")

    records = load_candidate_records(path)

    assert [record.candidate_id for record in records] == ["CAND_JSONL"]


def test_adapt_candidate_record_handles_nested_candidate_payload() -> None:
    nested = {
        "candidate": {
            "id": "CAND_NESTED",
            "name": "Nested Candidate",
            "resume": {"text": "Built production retrieval APIs with Python."},
            "profile": {"location": "Pune, India", "title": "AI Engineer"},
            "skills": ["Python", "Retrieval"],
        },
        "source": "ats-export",
    }

    record = adapt_candidate_record(nested)

    assert record.candidate_id == "CAND_NESTED"
    assert record.name == "Nested Candidate"
    assert "production retrieval" in record.raw_text
    assert record.metadata["schema_assumption"] == "nested candidate payload"


def test_load_candidate_records_rejects_duplicate_candidate_ids(tmp_path) -> None:
    path = tmp_path / "candidates.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(base_candidate("CAND_DUP")) + "\n")
        handle.write(json.dumps(base_candidate("CAND_DUP")) + "\n")

    with pytest.raises(ValueError, match="Duplicate candidate_id"):
        load_candidate_records(path)


def test_load_candidate_records_reports_malformed_jsonl_rows(tmp_path) -> None:
    path = tmp_path / "candidates.jsonl"
    path.write_text('{"candidate_id": "CAND_OK"}\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"line 2"):
        load_candidate_records(path)

