from __future__ import annotations

import csv
import gzip
import json

import pytest

from redrob_ranker.io import iter_candidates, write_audit, write_debug_scores, write_submission
from redrob_ranker.models import RankedCandidate, ScoreComponents, ScoredCandidate
from redrob_ranker.scoring import score_candidate, score_candidates
from redrob_ranker.validation import validate_submission
from tests.fixtures import base_candidate, keyword_stuffed_candidate


def test_write_submission_uses_required_header_and_rows(tmp_path) -> None:
    rows = [
        RankedCandidate("CAND_0000001", 1, 0.91234, "Strong applied ML fit."),
        RankedCandidate("CAND_0000002", 2, 0.81234, "Good adjacent fit."),
    ]
    output = tmp_path / "submission.csv"

    write_submission(rows, output)

    with output.open(encoding="utf-8", newline="") as handle:
        written = list(csv.reader(handle))

    assert written[0] == ["candidate_id", "rank", "score", "reasoning"]
    assert written[1] == ["CAND_0000001", "1", "0.9123", "Strong applied ML fit."]
    assert written[2] == ["CAND_0000002", "2", "0.8123", "Good adjacent fit."]


def test_write_submission_creates_parent_directory(tmp_path) -> None:
    output = tmp_path / "outputs" / "submission.csv"

    write_submission([RankedCandidate("CAND_0000001", 1, 10.0, "Reason.")], output)

    assert output.exists()


def test_write_debug_scores_includes_component_columns(tmp_path) -> None:
    scored = score_candidate(base_candidate())
    output = tmp_path / "debug.csv"

    write_debug_scores([scored], output)

    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["candidate_id"] == "CAND_0000001"
    assert rows[0]["role"] != ""
    assert rows[0]["retrieval"] != ""
    assert rows[0]["availability"] != ""
    assert rows[0]["risk"] != ""
    assert "hybrid search" in rows[0]["evidence_phrases"]


def test_write_audit_marks_top100_review_fields(tmp_path) -> None:
    good = score_candidate(base_candidate("CAND_0000001"))
    weak = score_candidate(keyword_stuffed_candidate("CAND_0000002"))
    output = tmp_path / "top100_audit.csv"

    write_audit(
        [
            RankedCandidate(good.candidate_id, 1, good.score, "Strong fit."),
            RankedCandidate(weak.candidate_id, 2, weak.score, "Weak fit."),
        ],
        {good.candidate_id: good, weak.candidate_id: weak},
        output,
    )

    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0].keys() >= {"candidate_id", "rank", "score", "verdict", "reason", "fix_needed"}
    assert rows[0]["verdict"] == "A"
    assert rows[1]["verdict"] in {"B", "C"}


@pytest.mark.parametrize("compressed", [False, True])
def test_iter_candidates_reads_jsonl_and_gzip(tmp_path, compressed: bool) -> None:
    path = tmp_path / ("candidates.jsonl.gz" if compressed else "candidates.jsonl")
    opener = gzip.open if compressed else open
    with opener(path, "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(base_candidate("CAND_0000001")) + "\n")
        handle.write("\n")
        handle.write(json.dumps(base_candidate("CAND_0000002")) + "\n")

    rows = list(iter_candidates(path))

    assert [row["candidate_id"] for row in rows] == ["CAND_0000001", "CAND_0000002"]


def test_iter_candidates_reports_invalid_json_line(tmp_path) -> None:
    path = tmp_path / "candidates.jsonl"
    path.write_text('{"candidate_id":"CAND_1"}\nnot-json\n', encoding="utf-8")

    with pytest.raises(ValueError, match=r"line 2"):
        list(iter_candidates(path))


def test_duplicate_candidate_ids_are_rejected() -> None:
    rows = [base_candidate("CAND_DUPLICATE"), base_candidate("CAND_DUPLICATE")]

    with pytest.raises(ValueError, match="Duplicate candidate_id"):
        score_candidates(rows)


def test_local_submission_validator_accepts_valid_output(tmp_path) -> None:
    output = tmp_path / "submission.csv"
    rows = [
        RankedCandidate(f"CAND_{index:07d}", index, 101.0 - index, f"Reason {index}.")
        for index in range(1, 101)
    ]
    write_submission(rows, output)

    validate_submission(output)


def test_local_submission_validator_rejects_bad_rank_order(tmp_path) -> None:
    output = tmp_path / "submission.csv"
    rows = [
        RankedCandidate(f"CAND_{index:07d}", index, 101.0 - index, f"Reason {index}.")
        for index in range(1, 101)
    ]
    rows[1] = RankedCandidate(rows[1].candidate_id, 9, rows[1].score, rows[1].reasoning)
    write_submission(rows, output)

    with pytest.raises(ValueError, match="expected rank 2"):
        validate_submission(output)
