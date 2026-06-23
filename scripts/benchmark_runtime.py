from __future__ import annotations

import argparse
import json
import platform
import sys
from copy import deepcopy
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.job_understanding import parse_job_description  # noqa: E402
from redrob_ranker.schema import load_candidate_records  # noqa: E402
from redrob_ranker.scoring import rank_scored_candidates, score_candidates  # noqa: E402


def run_benchmark(candidates_path: Path, job_path: Path | None, sizes: list[int], top_n: int) -> dict:
    base_records = [record.to_scoring_dict() for record in load_candidate_records(candidates_path)]
    if not base_records:
        raise ValueError("No candidates found for benchmark")
    job_text = job_path.read_text(encoding="utf-8") if job_path and job_path.exists() else ""
    role = parse_job_description(job_text) if job_text else None
    results = []
    for size in sizes:
        if size > 10000:
            results.append({"size": size, "status": "skipped", "reason": "size above default safe local benchmark cap"})
            continue
        candidates = duplicate_candidates(base_records, size)
        started = perf_counter()
        scored = score_candidates(candidates, role_requirements=role)
        ranked = rank_scored_candidates(scored, top_n=min(top_n, len(scored)))
        runtime = perf_counter() - started
        results.append(
            {
                "size": size,
                "status": "completed",
                "runtime_seconds": round(runtime, 6),
                "candidates_per_second": round(size / runtime, 2) if runtime > 0 else None,
                "top_n": len(ranked),
                "cpu_only": True,
                "network_calls": False,
                "paid_api": False,
            }
        )
    return {
        "project": "EvidenceGraph Ranker",
        "candidate_source": str(candidates_path),
        "job_source": str(job_path) if job_path else "",
        "machine_note": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
        "results": results,
    }


def duplicate_candidates(records: list[dict], size: int) -> list[dict]:
    duplicated = []
    for index in range(size):
        item = deepcopy(records[index % len(records)])
        item["candidate_id"] = f"BENCH_{index + 1:07d}"
        duplicated.append(item)
    return duplicated


def write_reports(report: dict, output_md: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json = output_md.with_suffix(".json")
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Performance Report",
        "",
        "Benchmark is local, CPU-only, deterministic, and uses no network or paid API calls.",
        "",
        f"- Candidate source: `{report['candidate_source']}`",
        f"- Job source: `{report['job_source'] or 'none'}`",
        f"- Machine note: {report['machine_note']}",
        "",
        "| Size | Status | Runtime seconds | Candidates/sec | Top N | Notes |",
        "|---:|---|---:|---:|---:|---|",
    ]
    for row in report["results"]:
        lines.append(
            "| {size} | {status} | {runtime} | {cps} | {top_n} | {notes} |".format(
                size=row["size"],
                status=row["status"],
                runtime=row.get("runtime_seconds", ""),
                cps=row.get("candidates_per_second", ""),
                top_n=row.get("top_n", ""),
                notes=row.get("reason", "CPU only; no network; no paid API"),
            )
        )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark EvidenceGraph Ranker runtime with duplicated candidate records.")
    parser.add_argument("--candidates", type=Path, default=ROOT / "data" / "candidates.jsonl")
    parser.add_argument("--job", type=Path, default=ROOT / "data" / "job.txt")
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 1000, 10000])
    parser.add_argument("--top-n", type=int, default=50)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / "performance_report.md")
    args = parser.parse_args()
    report = run_benchmark(args.candidates, args.job, args.sizes, args.top_n)
    write_reports(report, args.output)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
