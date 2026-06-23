# Performance

EvidenceGraph Ranker is a deterministic CPU-only ranker. It does not call paid APIs, LLM APIs, or external network services during ranking.

Run a local benchmark:

```powershell
python scripts/benchmark_runtime.py --candidates data/candidates.jsonl --job data/job.txt --sizes 100 1000 10000 --output outputs/performance_report.md
```

The benchmark duplicates available candidate records with unique IDs, runs scoring and ranking, and writes:

- `outputs/performance_report.md`
- `outputs/performance_report.json`

Sizes above the script's safe local cap are skipped and reported as skipped rather than faked.
