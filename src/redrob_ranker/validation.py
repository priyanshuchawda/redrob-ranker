from __future__ import annotations

import csv
import math
from pathlib import Path

from .io import HEADER


def validate_submission(path: str | Path, expected_rows: int = 100) -> None:
    submission_path = Path(path)
    with submission_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != HEADER:
            raise ValueError(f"Expected header {HEADER}, found {reader.fieldnames}")
        rows = list(reader)

    errors: list[str] = []
    if len(rows) != expected_rows:
        errors.append(f"expected {expected_rows} rows, found {len(rows)}")

    candidate_ids: set[str] = set()
    previous_score = math.inf
    for index, row in enumerate(rows, start=1):
        candidate_id = (row.get("candidate_id") or "").strip()
        if not candidate_id:
            errors.append(f"row {index}: empty candidate_id")
        elif candidate_id in candidate_ids:
            errors.append(f"row {index}: duplicate candidate_id {candidate_id}")
        candidate_ids.add(candidate_id)

        try:
            rank = int(row.get("rank") or "")
        except ValueError:
            errors.append(f"row {index}: rank is not an integer")
        else:
            if rank != index:
                errors.append(f"row {index}: expected rank {index}, found {rank}")

        try:
            score = float(row.get("score") or "")
        except ValueError:
            errors.append(f"row {index}: score is not numeric")
        else:
            if not math.isfinite(score):
                errors.append(f"row {index}: score must be finite")
            if score > previous_score:
                errors.append(f"row {index}: scores are not non-increasing")
            previous_score = score

        if not (row.get("reasoning") or "").strip():
            errors.append(f"row {index}: reasoning is empty")

    if errors:
        preview = "; ".join(errors[:10])
        if len(errors) > 10:
            preview += f"; and {len(errors) - 10} more error(s)"
        raise ValueError(preview)
