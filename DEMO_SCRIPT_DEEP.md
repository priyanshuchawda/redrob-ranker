# Deep Demo Script

## 1. 10 second pitch

EvidenceGraph Ranker takes a job description and candidate data, extracts a deterministic requirement matrix, ranks candidates by proof, confidence, hireability, and risk, and shows recruiters exactly what to verify next.

## 2. 30 second pitch

Most hiring tools improve resume search. EvidenceGraph Ranker improves hiring judgment. It keeps the Redrob challenge CSV path, then adds a product flow: JD matrix, normalized candidate ingestion, evidence extraction, claim/proof ledger, risk radar, review tags, backend comparison, Trust Audit, and exports. It runs locally with Python, FastAPI, Next.js, TypeScript, and Tailwind. No paid APIs or LLM calls are required.

## 3. 2 minute demo

1. Open `/dashboard`.
   - Say: “This is the Recruiter Intelligence Console.”
   - Show: KPI cards and JD Understanding.
2. Point to JD Matrix.
   - Say: “This is deterministic extraction, not LLM parsing.”
   - Show: must-have, strong signals, seniority, location, blockers.
3. Open `/run-ranking`.
   - Click: `Use Demo Scenario`.
   - Say: “Demo mode is intentional; fallback warning is separate.”
4. Open `/candidates`.
   - Show: `Review Tag`.
   - Say: “Recruiter sees why each candidate needs review.”
5. Open `/candidates/CAND_DEMO_001`.
   - Show: score breakdown and why shortlisted.
   - Say: “This candidate has career-backed production ranking proof.”
6. Show Evidence Ledger tabs.
   - Say: “Each item has claim/proof, source field, snippet, confidence and impact.”
7. Open `/compare`.
   - Compare: `CAND_DEMO_001` vs `CAND_DEMO_002`.
   - Say: “Backend comparison explains score, evidence, risk, and verification differences.”
8. Open `/trust-audit`.
   - Say: “Trust Audit exposes missing evidence and proxy warnings.”
9. Open `/exports`.
   - Show: JSON/CSV endpoints and generated files.

## 4. 5 minute demo

1. Run pre-demo commands:
   ```powershell
   python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
   python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 3
   python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
   python scripts/benchmark_runtime.py --candidates data/candidates.jsonl --job data/job.txt --sizes 100 1000 --output outputs/performance_report.md
   ```
2. Start backend:
   ```powershell
   uvicorn api.main:app --reload
   ```
3. Start frontend:
   ```powershell
   cd frontend
   npm run dev
   ```
4. Dashboard: show JD matrix, KPI cards, leaderboard, score breakdown.
5. Run Ranking: explain upload support and intentional demo mode.
6. Candidate detail: show score, reasoning, Evidence Ledger tabs, risks, missing evidence, review tags.
7. Compare: show backend-owned comparison result.
8. Trust Audit: show confidence/proof averages, high-risk count, missing evidence categories, proof-vs-claim summary.
9. Outputs: open `outputs/ranked_candidates.json`, `outputs/battlecards.md`, `outputs/evaluation_report.md`, `outputs/performance_report.md`.

## 5. Backup demo if backend fails

1. Use `/run-ranking` → `Use Demo Scenario`.
2. Explain that this is intentional demo mode.
3. Show static/demo payload in frontend.
4. Open local output files from `outputs/`.
5. State that fallback is visibly labeled and not silent.

## 6. Backup demo if frontend fails

Use CLI/API artifacts:

```powershell
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
python compare.py --job data/job.txt --candidates data/candidates.jsonl --a CAND_DEMO_001 --b CAND_DEMO_002 --output outputs/comparison_CAND_DEMO_001_vs_CAND_DEMO_002.json
python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 3
```

Open the JSON/Markdown files and explain the same flow.

## 7. What to say on every screen

- Landing: “This is the product shell; the core promise is evidence-based ranking.”
- Dashboard: “JD Understanding makes the system’s hiring intent visible.”
- Run Ranking: “Upload/paste data; demo mode is explicit; fallback is visible.”
- Candidates: “Review tags summarize why a recruiter should inspect a candidate.”
- Candidate detail: “The ledger is the audit trail.”
- Compare: “The backend explains why one candidate beats another.”
- Trust Audit: “This page shows risks and limitations, not just success.”
- Evaluation: “Without labels, metrics are proxy only.”
- Exports: “These are the generated submission/demo artifacts.”

## 8. Judge questions may come up

- Is it an LLM? No, deterministic Python heuristics.
- Are metrics real? Only if labels are supplied; current no-label evaluation is proxy.
- Does it use paid APIs? No.
- Can it handle real Redrob schema? Yes, demo `data/candidates.jsonl` follows Redrob shape and external challenge schema matches.
- Is upload production-hard? Partial; multipart works but large-file streaming is future work.

## 9. Best candidate pair to compare

Use `CAND_DEMO_001` vs `CAND_DEMO_002`.

- `CAND_DEMO_001`: stronger search/ranking proof.
- `CAND_DEMO_002`: adjacent ML platform/backend proof but weaker explicit ranking evidence.

## 10. What outputs to open

- `outputs/ranked_candidates.json`
- `outputs/ranked_candidates.csv`
- `outputs/evidence_ledgers.json`
- `outputs/battlecards.md`
- `outputs/comparison_CAND_DEMO_001_vs_CAND_DEMO_002.json`
- `outputs/evaluation_report.md`
- `outputs/performance_report.md`

## 11. Exact commands to run before demo

```powershell
pip install -r requirements.txt
cd frontend
npm install
cd ..
python -m pytest -q
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv --top-n 3
python validate.py outputs/submission.csv --expected-rows 3
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 3
python compare.py --job data/job.txt --candidates data/candidates.jsonl --a CAND_DEMO_001 --b CAND_DEMO_002 --output outputs/comparison_CAND_DEMO_001_vs_CAND_DEMO_002.json
python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
python scripts/benchmark_runtime.py --candidates data/candidates.jsonl --job data/job.txt --sizes 100 1000 --output outputs/performance_report.md
uvicorn api.main:app --reload
```

## 12. Exact browser pages to open

- `http://localhost:3000/dashboard`
- `http://localhost:3000/run-ranking`
- `http://localhost:3000/candidates`
- `http://localhost:3000/candidates/CAND_DEMO_001`
- `http://localhost:3000/compare`
- `http://localhost:3000/trust-audit`
- `http://localhost:3000/exports`

## 13. Risky things to avoid saying

- “Real recruiter accuracy” without labels.
- “LLM semantic parser.”
- “Production-ready large-file upload.”
- “Bias-free hiring.”
- “The system replaces recruiter judgment.”
- “Evidence is externally verified.”
