from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.comparison import compare_scored_candidates  # noqa: E402
from redrob_ranker.job_understanding import default_role_requirements, parse_job_description  # noqa: E402
from redrob_ranker.scoring import score_candidates  # noqa: E402
from redrob_ranker.schema import load_candidate_records  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two candidates using EvidenceGraph Ranker.")
    parser.add_argument("--job", help="Optional job description text file")
    parser.add_argument("--candidates", required=True, help="Candidate input file")
    parser.add_argument("--a", required=True, help="Candidate A id")
    parser.add_argument("--b", required=True, help="Candidate B id")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    matrix = parse_job_description(Path(args.job).read_text(encoding="utf-8")) if args.job else default_role_requirements()
    records = load_candidate_records(args.candidates)
    scored = score_candidates(
        [record.to_scoring_dict() for record in records],
        reference_date=date(2026, 6, 17),
        role_requirements=matrix if args.job else None,
    )
    by_id = {row.candidate_id: row for row in scored}
    if args.a not in by_id:
        parser.error(f"candidate not found: {args.a}")
    if args.b not in by_id:
        parser.error(f"candidate not found: {args.b}")
    result = compare_scored_candidates(by_id[args.a], by_id[args.b], role_requirements=matrix)
    rendered = json.dumps(result, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Wrote comparison to {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

