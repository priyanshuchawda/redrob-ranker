from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.battlecards import write_battlecards  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate recruiter battle cards from ranked product JSON.")
    parser.add_argument("--ranking", required=True, help="Path to ranked_candidates.json")
    parser.add_argument("--output", required=True, help="Path to battlecards.md")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    write_battlecards(args.ranking, args.output, top_n=args.top_n)
    print(f"Wrote battle cards to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

