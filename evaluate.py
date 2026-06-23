from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.evaluation import evaluate_payload, render_evaluation_report  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate ranked candidates with labels or proxy checks.")
    parser.add_argument("--ranking", help="Path to ranked_candidates.json")
    parser.add_argument("--labels", help="Optional JSON mapping candidate_id to relevance label")
    parser.add_argument("--output", default="outputs/evaluation_report.md", help="Markdown report path")
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--candidates", help="Accepted for compatibility; labels are required for real metrics")
    args = parser.parse_args()

    ranking_path = Path(args.ranking or "outputs/ranked_candidates.json")
    payload = json.loads(ranking_path.read_text(encoding="utf-8"))
    labels = json.loads(Path(args.labels).read_text(encoding="utf-8")) if args.labels else None
    result = evaluate_payload(payload, labels=labels, top_n=args.top_n)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_evaluation_report(result), encoding="utf-8")
    print(f"Wrote {result['mode']} evaluation report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

