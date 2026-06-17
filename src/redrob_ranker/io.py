from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Iterable, Iterator

from .models import RankedCandidate

HEADER = ["candidate_id", "rank", "score", "reasoning"]


def iter_candidates(path: str | Path) -> Iterator[dict]:
    candidate_path = Path(path)
    opener = gzip.open if candidate_path.suffix == ".gz" else open
    with opener(candidate_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def write_submission(rows: Iterable[RankedCandidate], output_path: str | Path) -> None:
    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for row in rows:
            writer.writerow([row.candidate_id, row.rank, f"{row.score:.4f}", row.reasoning])

