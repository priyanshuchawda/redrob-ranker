from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.io import iter_candidates, write_audit, write_debug_scores, write_submission  # noqa: E402
from redrob_ranker.scoring import rank_scored_candidates, score_candidates  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank Redrob challenge candidates.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--top-n", type=int, default=100, help="Number of rows to emit")
    parser.add_argument(
        "--reference-date",
        type=date.fromisoformat,
        default=date(2026, 6, 17),
        help="Dataset snapshot date for recency signals (default: 2026-06-17)",
    )
    parser.add_argument("--debug-out", help="Optional local CSV with all scored candidates and component scores")
    parser.add_argument("--audit-out", help="Optional local CSV for reviewing the emitted top-N candidates")
    args = parser.parse_args()

    started = perf_counter()
    scored = score_candidates(iter_candidates(args.candidates), reference_date=args.reference_date)
    if len(scored) < args.top_n:
        parser.error(f"requested --top-n {args.top_n}, but only {len(scored)} candidates were loaded")
    ranked = rank_scored_candidates(scored, top_n=args.top_n)
    write_submission(ranked, args.out)
    if args.debug_out:
        write_debug_scores(scored, args.debug_out)
    if args.audit_out:
        write_audit(ranked, {row.candidate_id: row for row in scored}, args.audit_out)
    elapsed = perf_counter() - started
    print(f"Ranked {len(scored):,} candidates and wrote {len(ranked)} rows to {args.out} in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
