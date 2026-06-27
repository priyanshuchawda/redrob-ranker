# EvidenceGraph Ranker

EvidenceGraph Ranker is a deterministic candidate-ranking system for the Redrob Intelligent Candidate Discovery challenge. It ranks the top candidates for the supplied Senior AI Engineer job description using profile evidence, career history, skills, behavioral signals, availability, location fit, and risk checks.

The ranking step is CPU-only, local, repeatable, and does not call hosted APIs.

## What the system does

- Reads the official `candidates.jsonl` candidate pool.
- Reads the supplied job description from `.docx` or `.txt`.
- Extracts role-fit, retrieval/ranking/evaluation evidence, production proof, seniority, behavioral signals, and risk flags.
- Penalizes keyword stuffing, weak proof, impossible skill claims, stale profiles, low response likelihood, and location/logistics blockers.
- Produces a ranked top-100 submission with grounded 1-2 sentence reasoning.
- Exports both the official CSV format and an XLSX version for portals that request spreadsheets.
- Includes a FastAPI backend and Next.js recruiter console for local review.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Frontend setup:

```powershell
cd frontend
npm install
npm run dev
```

## Official ranking command

From the repo root:

```powershell
python rank.py --job "D:\Users\pares\Desktop\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\job_description.docx" --candidates "D:\Users\pares\Desktop\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl" --out outputs\final_submission.csv --top-n 100
```

Validate the CSV:

```powershell
python "D:\Users\pares\Desktop\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\validate_submission.py" outputs\final_submission.csv "D:\Users\pares\Desktop\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
```

Create the XLSX upload file:

```powershell
python scripts\export_submission_xlsx.py --csv outputs\final_submission.csv --xlsx outputs\final_submission.xlsx
```

The current final XLSX artifact is included at:

```text
submission/redrob_ranked_output.xlsx
```

## Output format

The official CSV and XLSX both contain:

```text
candidate_id,rank,score,reasoning
```

Rules enforced:

- exactly 100 ranked rows;
- ranks 1 through 100 appear once;
- candidate IDs are unique;
- scores are non-increasing by rank;
- reasoning is candidate-specific and grounded in supplied fields.

## Local product outputs

For richer local inspection:

```powershell
python rank.py --job data\job.txt --candidates data\candidates.jsonl --output outputs\ranked_candidates.json --csv-out outputs\ranked_candidates.csv --top-n 50 --audit
```

This creates JSON/CSV outputs, evidence ledgers, runtime summary, data-quality report, and a top-candidate audit file under `outputs/`.

## Backend

```powershell
uvicorn api.main:app --reload
```

Useful endpoints:

- `GET /api/health`
- `POST /api/rank`
- `GET /api/rank/latest`
- `POST /api/rank/upload`
- `GET /api/candidates`
- `GET /api/candidates/{candidate_id}`
- `POST /api/compare`
- `POST /api/evaluate`
- `GET /api/exports/ranked-json`
- `GET /api/exports/ranked-csv`

## Frontend

The local recruiter console includes:

- dashboard;
- run-ranking page;
- ranked candidates table;
- candidate detail page;
- candidate comparison;
- evaluation view;
- trust audit;
- export page.

The UI is for inspection and explanation. The official submission artifact is produced by `rank.py`.

## Verification

```powershell
python -m pytest -q
cd frontend
npm run build
```

Verified locally:

- Python tests pass.
- Frontend production build passes.
- Official dataset ranking creates 100 rows.
- Official validator accepts the generated CSV.
- XLSX export opens as a clean spreadsheet with the required columns.

## Architecture

```text
official dataset + job description
        ↓
schema ingestion and data-quality checks
        ↓
feature extraction from profile, skills, career history, and Redrob signals
        ↓
evidence-weighted scoring with risk penalties
        ↓
deterministic ranking and tie-breaks
        ↓
CSV/XLSX submission + local review UI
```

Core modules:

- `src/redrob_ranker/schema.py` — flexible candidate ingestion.
- `src/redrob_ranker/features.py` — role, proof, behavior, logistics, and risk feature extraction.
- `src/redrob_ranker/scoring.py` — scoring, normalization, and deterministic ranking.
- `src/redrob_ranker/reasoning.py` — grounded candidate reasoning.
- `src/redrob_ranker/evidence_ledger.py` — proof/missing-evidence ledger.
- `src/redrob_ranker/risk.py` — structured risk radar.
- `src/redrob_ranker/comparison.py` — candidate A/B comparison.

## Notes

- No manual edits are needed after running the ranking command.
- The generated CSV is the challenge-spec artifact.
- The XLSX export is provided only for upload forms that ask for a spreadsheet file.
