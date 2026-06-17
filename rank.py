from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.io import iter_candidates, write_submission  # noqa: E402
from redrob_ranker.scoring import rank_candidates  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank Redrob challenge candidates.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--top-n", type=int, default=100, help="Number of rows to emit")
    parser.add_argument("--reference-date", default="2026-06-17", help="YYYY-MM-DD date for recency signals")
    args = parser.parse_args()

    reference_date = date.fromisoformat(args.reference_date)
    ranked = rank_candidates(iter_candidates(args.candidates), reference_date=reference_date, top_n=args.top_n)
    write_submission(ranked, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

