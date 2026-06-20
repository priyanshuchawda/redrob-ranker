from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.validation import validate_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a generated Redrob submission CSV.")
    parser.add_argument("submission", help="Path to submission.csv")
    parser.add_argument("--expected-rows", type=int, default=100)
    args = parser.parse_args()

    try:
        validate_submission(args.submission, expected_rows=args.expected_rows)
    except (OSError, ValueError) as exc:
        print(f"Invalid submission: {exc}", file=sys.stderr)
        return 1

    print(f"Submission is structurally valid: {args.submission}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
