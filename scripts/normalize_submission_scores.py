from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDNAMES = ["candidate_id", "rank", "score", "reasoning"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Redrob submission scores to a 0-1 descending scale.")
    parser.add_argument("csv_path", help="Submission CSV to normalize in place")
    args = parser.parse_args()
    path = Path(args.csv_path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("submission CSV has no rows")
    count = len(rows)
    for row in rows:
        rank = int(row["rank"])
        row["score"] = f"{_score_for_rank(rank, count):.4f}"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Normalized {count} rows in {path}")
    return 0


def _score_for_rank(rank: int, count: int) -> float:
    if count <= 1:
        return 1.0
    return max(0.0, min(1.0, 0.99 - ((rank - 1) * (0.98 / (count - 1)))))


if __name__ == "__main__":
    raise SystemExit(main())
