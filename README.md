# EvidenceGraph Ranker

EvidenceGraph Ranker is a deterministic recruiting intelligence product. It keeps the original Redrob challenge CSV ranker and adds JD understanding, flexible ingestion, product JSON output, evidence ledgers, battle cards, candidate comparison, structured risk radar, responsible ranking documentation, a FastAPI backend, and a Next.js Recruiter Intelligence Console.

## Why It Is Different

Most hiring tools improve resume search. EvidenceGraph Ranker improves hiring judgment.

It ranks candidates by role fit, proof strength, confidence, hireability, and risk instead of raw resume keyword overlap. Claims such as "Python" in a skill list are separated from proof such as "shipped a production API using Python and FastAPI." Explanations are generated from candidate fields only, or marked unclear.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Old Challenge CSV Command

This command is preserved:

```powershell
python rank.py --candidates candidates.jsonl --out submission.csv
```

Demo validation:

```powershell
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv --top-n 3
python validate.py outputs/submission.csv --expected-rows 3
```

The legacy CSV still contains:

```text
candidate_id,rank,score,reasoning
```

## Product Ranking Command

```powershell
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
```

Generated product files include:

- `outputs/ranked_candidates.json`
- `outputs/ranked_candidates.csv`
- `outputs/evidence_ledgers.json`
- `outputs/data_quality_report.json`
- `outputs/runtime_summary.json`
- `outputs/top_candidates_audit.csv`

## Battle Cards

```powershell
python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 10
```

## Candidate Comparison

```powershell
python compare.py --job data/job.txt --candidates data/candidates.jsonl --a CAND_DEMO_001 --b CAND_DEMO_002
```

## Evaluation

Proxy evaluation without labels:

```powershell
python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
```

Real labeled evaluation requires labels:

```powershell
python evaluate.py --ranking outputs/ranked_candidates.json --labels data/labels.example.json --output outputs/evaluation_report.md --top-n 4
```

If labels are not supplied, reports are explicitly labeled synthetic/proxy and must not be read as real recruiter accuracy.

## Backend

```powershell
uvicorn api.main:app --reload
```

Key endpoints:

- `GET /api/health`
- `GET /api/demo-data`
- `POST /api/rank`
- `GET /api/candidates`
- `GET /api/candidates/{candidate_id}`
- `POST /api/compare`
- `POST /api/evaluate`
- `GET /api/exports/ranked-json`
- `GET /api/exports/ranked-csv`

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The Recruiter Intelligence Console includes dashboard, run ranking, candidates, candidate detail, compare, evaluation, and exports pages. It calls the FastAPI backend when available and uses bundled demo output as a local fallback.

## Validation

```powershell
python -m pytest -q
python -c "from api.main import app; print(app.title)"
cd frontend
npm run build
```

Current local verification:

- `python -m pytest -q`: 67 passed.
- Legacy CSV demo command: passed.
- Local validator on demo CSV: passed.
- Product ranking command: passed.
- Battle card command: passed.
- Comparison command: passed.
- Proxy evaluation command: passed.
- FastAPI import and test-client smoke check: passed.
- `frontend/npm run build`: passed.

## Architecture

Core package modules:

- `features.py`: deterministic evidence extraction.
- `scoring.py`: calibrated scoring plus optional JD-aware adjustments.
- `job_understanding.py`: deterministic RoleRequirementMatrix parsing.
- `schema.py`: flexible candidate ingestion and data quality reporting.
- `evidence_ledger.py`: claim/proof evidence ledger.
- `risk.py`: structured risk radar.
- `reasoning.py`: grounded challenge and product explanations.
- `comparison.py`: candidate A/B comparison.
- `battlecards.py`: recruiter battle cards.
- `evaluation.py`: labeled or proxy evaluation reporting.

See `docs/architecture.md`, `docs/scoring_methodology.md`, `docs/evidence_graph.md`, `docs/responsible_ranking.md`, and `docs/evaluation.md`.

## Limitations

- JD parsing is deterministic and heuristic; it is not an LLM parser.
- The frontend fallback data is demo-only; live product data comes from FastAPI.
- Proxy evaluation is not real recruiter accuracy.
- File upload is implemented in the frontend text/file control and JSON API path; multipart backend upload can be expanded later.
- The ranking path remains CPU-only and deterministic by default.

## Future Improvements

- Add richer JD section parsing and configurable scoring profiles.
- Add persistent run storage for API sessions.
- Add multipart uploads for large files in the backend.
- Add visual diff exports for comparison reports.
- Calibrate product score normalization on a larger labeled benchmark when real labels are available.
