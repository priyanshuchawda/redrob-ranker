# Redrob Senior AI Engineer Candidate Ranker

CPU-only, no-network ranker for the Redrob Intelligent Candidate Discovery challenge.

## Run

```powershell
python rank.py --candidates "..\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\candidates.jsonl" --out submission.csv
```

## Test

```powershell
python -m pytest -q
```

## Method

The ranker uses deterministic feature scoring rather than hosted LLM calls. It rewards career-history evidence for production ML, retrieval, ranking, search, recommendations, evaluation, and product engineering. It down-weights keyword-stuffed profiles, suspicious skill claims, weak availability signals, pure services trajectories, poor location fit, and other risk indicators.

The generated `reasoning` column is built from candidate fields only, so every claim can be traced back to the profile.

