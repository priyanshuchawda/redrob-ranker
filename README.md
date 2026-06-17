# Redrob Senior AI Engineer Candidate Ranker

CPU-only, no-network ranker for the Redrob Intelligent Candidate Discovery challenge.

## Reproduce

Install the single test dependency:

```powershell
python -m pip install -r requirements.txt
```

Run the ranker:

```powershell
python rank.py --candidates "..\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\candidates.jsonl" --out submission.csv
```

Validate the generated file with the challenge validator:

```powershell
python "..\\[PUB] India_runs_data_and_ai_challenge\\India_runs_data_and_ai_challenge\\validate_submission.py" submission.csv
```

On the development machine, the full 100K-candidate run completed in 173.25 seconds on CPU after the expanded evidence/risk pass.

## Tests

```powershell
python -m pytest --rootdir . -q
```

Current status: 17 tests passing.

## Method

The ranker uses deterministic feature scoring rather than hosted LLM calls. It rewards career-history evidence for production ML, retrieval, ranking, search, recommendations, evaluation, product engineering, and plain-language relevance-system work. It down-weights keyword-stuffed profiles, suspicious skill claims, weak availability signals, pure services trajectories, non-target ML domains, poor location fit, and other risk indicators.

The generated `reasoning` column is built from candidate fields only, so every claim can be traced back to the profile.

## Architecture

- `rank.py`: CLI entrypoint.
- `src/redrob_ranker/io.py`: JSONL/GZIP streaming and CSV writing.
- `src/redrob_ranker/features.py`: profile, career, skills, logistics, behavior, and risk extraction.
- `src/redrob_ranker/scoring.py`: weighted deterministic score and tie-broken ranking.
- `src/redrob_ranker/reasoning.py`: grounded 1-2 sentence explanations.
- `tests/`: behavior tests for extraction, scoring, reasoning, and output format.

## No-Network Guarantee

The ranking path uses only Python standard-library code. It does not call hosted LLMs, external embedding APIs, web services, GPUs, or remote databases.
