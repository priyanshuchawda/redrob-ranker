# EvidenceGraph Ranker Productization Plan

## Baseline Findings

- The existing project is a deterministic Python ranking engine for the Redrob challenge.
- The old challenge command is implemented by `rank.py` and depends on `src/redrob_ranker/io.py`, `features.py`, `scoring.py`, `reasoning.py`, and `validation.py`.
- Current supported input is JSONL and JSONL.GZ via `iter_candidates`.
- Current output contract is `candidate_id,rank,score,reasoning`; this must remain unchanged for `--out`.
- Existing strengths to preserve: deterministic scoring, grounded reasoning, duplicate ID rejection, malformed JSON errors, debug CSV, audit CSV, validation, and 46 passing tests.
- Existing weakness: the calibrated engine does not accept a real job description and does not expose product-grade JSON, evidence ledgers, comparison, API, or UI.

## Architecture

The upgrade will keep the current scoring path intact and add a product layer around it:

1. `job_understanding.py` parses a JD into a deterministic `RoleRequirementMatrix`.
2. `schema.py` adapts JSONL, JSONL.GZ, JSON, CSV, and nested records into canonical candidate dictionaries while preserving raw records.
3. `scoring.py` accepts an optional role matrix and emits normalized product score fields without removing existing component scores.
4. `risk.py`, `evidence_ledger.py`, and `reasoning.py` turn existing feature evidence into structured risk radar entries, claim/proof evidence, and richer recruiter explanations.
5. `io.py` keeps the legacy challenge writers and gains product JSON/CSV/evidence/data-quality/runtime writers.
6. `rank.py` supports both the old `--out` path and the new `--job/--output/--csv-out/--audit` product path.
7. `battlecards.py`, `compare.py`, and `evaluate.py` expose product workflows.
8. `api/` wraps the package with FastAPI routes and service code.
9. `frontend/` provides a Next.js Recruiter Intelligence Console with demo fallback and API integration.

## Files to Extend

- `rank.py`: extend CLI flags while preserving required legacy behavior.
- `src/redrob_ranker/models.py`: add product score fields and structured output dataclasses.
- `src/redrob_ranker/config.py`: add JD-aware calibration knobs.
- `src/redrob_ranker/scoring.py`: add optional role matrix adjustments and normalized product scores.
- `src/redrob_ranker/io.py`: extend ingestion/writers while keeping existing functions stable.
- `src/redrob_ranker/reasoning.py`: keep legacy `generate_reasoning`, add structured reasoning helpers.
- `scripts/synthetic_evaluation.py`: keep current proxy evaluation and expose richer labeled/proxy reporting.
- `README.md`, `SUBMISSION.md`, and docs: update without deleting challenge context.

## Files to Add

- `src/redrob_ranker/job_understanding.py`
- `src/redrob_ranker/schema.py`
- `src/redrob_ranker/evidence_ledger.py`
- `src/redrob_ranker/battlecards.py`
- `src/redrob_ranker/comparison.py`
- `src/redrob_ranker/risk.py`
- `src/redrob_ranker/fairness.py`
- `src/redrob_ranker/evaluation.py`
- `battlecards.py`
- `compare.py`
- `evaluate.py`
- `api/main.py`
- `api/schemas.py`
- `api/routes/ranking.py`
- `api/routes/candidates.py`
- `api/routes/compare.py`
- `api/routes/evaluation.py`
- `api/routes/exports.py`
- `api/services/ranker_service.py`
- `frontend/` Next.js app files
- `docs/architecture.md`
- `docs/evidence_graph.md`
- `docs/responsible_ranking.md`
- `docs/evaluation.md`
- `docs/demo_script.md`
- `FINAL_REPORT.md`
- `FINAL_TECHNICAL_AUDIT.md`
- Demo data under `data/`

## Implementation Tasks

1. Add tests for JD parsing and default fallback matrix.
2. Add tests for JSON, CSV, JSONL, JSONL.GZ, nested records, malformed rows, duplicate IDs, and data quality reports.
3. Add tests for JD-aware scoring and required normalized score outputs.
4. Add tests for fairness filtering and the `ranking_uses_role_relevant_evidence_only` metadata flag.
5. Add tests for evidence ledger generation, including claim versus proof separation.
6. Add tests for richer reasoning fields and structured risk radar entries.
7. Add tests for product JSON output, product CSV output, and old challenge CSV compatibility.
8. Add tests for battle card generation and candidate comparison.
9. Add a FastAPI health endpoint test if dependencies are available.
10. Implement the smallest production code needed to pass those tests, preserving existing public functions.
11. Create demo JD and candidate data that use real fields from the current schema.
12. Build a static, local-friendly Next.js frontend that fetches FastAPI when available and falls back to bundled demo data.
13. Update evaluation to distinguish real labeled metrics from synthetic/proxy metrics.
14. Update README, SUBMISSION, docs, final report, and technical audit.
15. Run `python -m pytest -q`, old CLI command, new product CLI command, battlecards, comparison, evaluation, and backend import/start checks.

## Compatibility Rules

- `python rank.py --candidates candidates.jsonl --out submission.csv` remains valid.
- Existing CSV header and row formatting remain unchanged.
- Existing tests remain in place and must pass.
- Scoring remains deterministic by default.
- No Streamlit files are added.
- No paid API or network dependency is required for ranking.
- Evidence and explanations must be derived from candidate fields or clearly marked unclear.
- Synthetic/proxy evaluation must not be described as real recruiter accuracy.

## Verification Commands

```powershell
python -m pytest -q
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv --top-n 3
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 3 --audit
python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 3
python compare.py --job data/job.txt --candidates data/candidates.jsonl --a CAND_DEMO_001 --b CAND_DEMO_002
python evaluate.py --candidates data/candidates.jsonl --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md
python -c "from api.main import app; print(app.title)"
```
