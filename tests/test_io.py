from __future__ import annotations

import csv

from redrob_ranker.io import write_submission
from redrob_ranker.models import RankedCandidate


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

