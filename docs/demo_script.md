# Two Minute Judge Demo

## 10 second product explanation

“Most hiring tools improve resume search. EvidenceGraph Ranker improves hiring judgment: JD in, deterministic requirement matrix out, candidates ranked by proof, confidence, hireability and risk, with an audit trail for what to verify next.”

## Exact local commands

```powershell
pip install -r requirements.txt
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 4 --audit
python scripts/benchmark_runtime.py --candidates data/candidates.jsonl --job data/job.txt --sizes 100 1000 --output outputs/performance_report.md
uvicorn api.main:app --reload
cd frontend
npm install
npm run dev
```

## Walkthrough

1. Open `http://localhost:3000/dashboard`.
2. Say: “This first card is JD Understanding — a deterministic requirement matrix, not an LLM claim.”
3. Show must-have skills, strong signals, seniority, location, availability and blockers.
4. Open `/run-ranking`.
5. Click `Use Demo Scenario`.
6. Say: “This is intentional demo mode, not a hidden fallback. Fallback warning only appears if live ranking fails.”
7. Run live ranking if backend is running.
8. Open Candidates and point to the `Review Tag` column.
9. Open `CAND_DEMO_001`.
10. Show “Why not higher” tags.
11. Show Evidence Ledger tabs: positive evidence, negative evidence, missing evidence and risks.
12. Say: “Each item shows claim/proof, source field, exact snippet, confidence and score impact.”
13. Show Risk Radar.
14. Open Compare and compare `CAND_DEMO_001` vs `CAND_DEMO_002`.
15. Say: “The comparison is backend-owned; the frontend renders the decision.”
16. Open Trust Audit.
17. Say: “This page makes limitations visible: missing evidence, low confidence, location risk and proxy warning.”
18. Open Exports and show JSON/CSV/battle-card outputs.

## What to avoid saying

- Do not claim real recruiter accuracy unless real labels are supplied.
- Do not call JD parsing an LLM parser.
- Do not say the frontend persists runs; backend latest run is in-memory.
- Do not say large multipart uploads are production-hardened.

## Backup plan if API fails

1. Click `Use Demo Scenario` on Run Ranking.
2. Show dashboard and candidate detail from bundled demo data.
3. Open generated `outputs/ranked_candidates.json`, `outputs/battlecards.md`, and `outputs/performance_report.md`.
4. Explain that degraded fallback is visibly labeled and not silent.
