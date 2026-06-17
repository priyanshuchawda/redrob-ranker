from __future__ import annotations

import csv

from redrob_ranker.io import write_audit, write_debug_scores, write_submission
from redrob_ranker.models import RankedCandidate, ScoreComponents, ScoredCandidate
from redrob_ranker.scoring import score_candidate
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
