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
- `GET /api/rank/latest`
- `POST /api/rank/upload`
- `GET /api/candidates`
- `GET /api/candidates/{candidate_id}`
- `POST /api/compare`
- `POST /api/evaluate`
- `GET /api/exports/ranked-json`
- `GET /api/exports/ranked-csv`

Multipart ranking accepts a candidate file in JSONL, JSONL.GZ, JSON, or CSV format plus either `job_text` or an uploaded UTF-8 job file. The original JSON endpoint remains available.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The Recruiter Intelligence Console uses Next.js, TypeScript, and Tailwind CSS. It includes dashboard, run ranking, candidates, candidate detail, compare, evaluation, and exports pages. Candidate comparison calls the backend comparison engine and renders score, evidence, risk, and recruiter-verification differences. When live ranking fails, bundled demo output remains available behind a visible degraded-mode warning.

## Judge Demo Proof

Screenshots:

- Add landing page screenshot here after running the local demo.
- Add JD Requirement Matrix screenshot here after running the local demo.
- Add Evidence Ledger screenshot here after running the local demo.
- Add Trust Audit screenshot here after running the local demo.

Demo video:

- Add demo video link here after recording the local walkthrough.

Two-minute path:

1. Open `/dashboard` and show JD Understanding.
2. Open `/run-ranking` and click `Use Demo Scenario` to show intentional demo mode.
3. Run live ranking if the backend is available.
4. Open the leaderboard and point to the `Review Tag` column.
5. Open `CAND_DEMO_001` and show the full Evidence Ledger.
6. Open Compare and compare `CAND_DEMO_001` with `CAND_DEMO_002`.
7. Open Trust Audit and show proof, confidence, missing evidence, and risk counts.
8. Open Exports and show generated JSON/CSV/battle-card assets.

What is real:

- Deterministic Python ranking engine.
- JD requirement matrix extraction.
- Product JSON and legacy CSV outputs.
- Evidence ledgers, risk radar, review tags, comparison, trust audit, and benchmark script.
- FastAPI backend and Next.js/Tailwind frontend.

What is proxy:

- Evaluation without labels is proxy only.
- Demo scenario is intentional sample data, not recruiter accuracy.

Architecture in one line:

`candidate/job files -> deterministic Python engine -> evidence/risk/score payload -> FastAPI -> Recruiter Intelligence Console`.

## Validation

```powershell
python -m pytest -q
python -c "from api.main import app; print(app.title)"
cd frontend
npm run build
```

Current local verification:

- `python -m pytest -q`: 73 passed.
- Legacy CSV demo command: passed.
- Local validator on demo CSV: passed.
- Product ranking command: passed.
- Battle card command: passed.
- Comparison command: passed.
- Proxy evaluation command: passed.
- FastAPI import and test-client smoke check: passed.
- Multipart JSONL ranking upload: passed.
- Browser comparison and explicit fallback-warning checks: passed.
- `frontend/npm run build`: passed.

## Architecture

Core package modules:

- `features.py`: deterministic evidence extraction.
- `scoring.py`: calibrated scoring plus optional JD-aware adjustments.
- `job_understanding.py`: deterministic JD requirement matrix extraction.
- `schema.py`: flexible candidate ingestion and data quality reporting.
- `evidence_ledger.py`: claim/proof evidence ledger.
- `risk.py`: structured risk radar.
- `reasoning.py`: grounded challenge and product explanations.
- `comparison.py`: candidate A/B comparison.
- `battlecards.py`: recruiter battle cards.
- `evaluation.py`: labeled or proxy evaluation reporting.

See `docs/architecture.md`, `docs/scoring_methodology.md`, `docs/evidence_graph.md`, `docs/responsible_ranking.md`, and `docs/evaluation.md`.

## Limitations

- JD requirement matrix extraction is deterministic and heuristic; it is not an LLM parser.
- The frontend fallback data is demo-only; live product data comes from FastAPI.
- Proxy evaluation is not real recruiter accuracy.
- Multipart uploads are buffered in memory before deterministic parsing, so very large files need production hardening.
- The ranking path remains CPU-only and deterministic by default.
- The Trust Audit page summarizes the latest in-memory ranking payload; it is not persisted across backend restarts.
- Browser demo mode is intentionally separate from degraded fallback.

## Runtime Benchmark

```powershell
python scripts/benchmark_runtime.py --candidates data/candidates.jsonl --job data/job.txt --sizes 100 1000 10000 --output outputs/performance_report.md
```

Latest local benchmark using the external sample dataset path:

- 100 candidates: 0.314559s, 317.9 candidates/sec.
- 1000 candidates: 3.027267s, 330.33 candidates/sec.
- CPU only, no network calls, no paid API.

## Future Improvements

- Add richer JD section parsing and configurable scoring profiles.
- Add persistent run storage for API sessions.
- Add streaming object storage and background processing for very large uploads.
- Add visual diff exports for comparison reports.
- Calibrate product score normalization on a larger labeled benchmark when real labels are available.
