# EvidenceGraph Ranker — Project Deep Dive

## 1. Executive summary

EvidenceGraph Ranker is a deterministic recruiting intelligence product for the Redrob candidate ranking challenge. It is used by a recruiter or judge to turn a job description and candidate data into a ranked shortlist. Inputs are a JD text file/string plus candidates in JSONL, JSONL.GZ, JSON, CSV, or nested JSON records. Outputs include legacy challenge CSV, product JSON, product CSV, evidence ledgers, battle cards, comparison JSON, evaluation reports, audit files, and runtime reports. It differs from keyword matching by separating claimed skills from career-backed proof, adding risk and hireability signals, and showing source snippets. It is useful because recruiters can see why a candidate ranked, what is missing, and what to verify next.

## 2. One line project positioning

1. EvidenceGraph Ranker turns candidate screening into evidence-based hiring judgment.
2. EvidenceGraph Ranker ranks candidates by proof, confidence, hireability, and risk—not keyword overlap.
3. EvidenceGraph Ranker gives recruiters a shortlist with an audit trail.
4. EvidenceGraph Ranker separates candidate claims from career-backed proof.
5. EvidenceGraph Ranker makes ranking decisions explainable enough for recruiter review.

## 3. Problem being solved

- Keyword stuffing: candidates can list many AI/backend terms without showing real project or career proof.
- Resume search limitations: exact-match search misses plain-language evidence and cannot reliably compare proof depth.
- Weak proof behind strong claims: a profile can claim Python, LLM, or ranking skills while career history shows only demos or adjacent exposure.
- Lack of explainability: many rankers return a score but not source fields, snippets, missing evidence, or interview focus.
- Hiring feasibility: availability, location, relocation, responsiveness, and notice period matter but are usually separate from relevance.
- Risk and missing evidence: recruiters need to know what reduced confidence before interviewing.
- Recruiter decision fatigue: a ranked table plus battle cards, review tags, and comparison reduces manual triage burden.

## 4. Solution overview

1. JD requirement matrix: `src/redrob_ranker/job_understanding.py` parses deterministic `RoleRequirementMatrix` fields.
2. Candidate ingestion: `src/redrob_ranker/schema.py` loads JSONL, JSONL.GZ, JSON, CSV, and nested payloads.
3. Candidate normalization: `CandidateRecord.to_scoring_dict()` preserves raw records and maps best-effort fields into the Redrob scoring shape.
4. Evidence extraction: `src/redrob_ranker/features.py` extracts role, skill, production, engineering, leadership, availability, logistics, and risk signals.
5. Claim versus proof: `src/redrob_ranker/evidence_ledger.py` labels skills/profile items as claims and career/production snippets as proof or strong proof.
6. Scoring: `src/redrob_ranker/scoring.py` builds internal `ScoreComponents` and normalized `ProductScores`.
7. Risk radar: `src/redrob_ranker/risk.py` maps risk flags into structured risk items.
8. Evidence ledger: `build_evidence_ledger()` creates positive evidence, negative evidence, missing evidence, source fields, score impacts, and interview focus.
9. Battle cards: `src/redrob_ranker/battlecards.py` creates recruiter-ready Markdown summaries from product JSON.
10. Candidate comparison: `src/redrob_ranker/comparison.py` compares scores, evidence, risks, and verification prompts.
11. Exports: `src/redrob_ranker/io.py` writes CSV/JSON/evidence/runtime artifacts.
12. UI: `frontend/` renders dashboard, JD matrix, candidate table, detail, compare, trust audit, evaluation, exports, and run-ranking upload/demo paths.

## 5. What is actually implemented

| Feature | Implemented status | Where in code | How it works | Demo visibility | Judge value |
|---|---|---|---|---|---|
| Legacy CSV ranker | Implemented | `rank.py`, `io.write_submission`, `validation.py` | `--out` writes `candidate_id,rank,score,reasoning` | CLI + `outputs/submission.csv` | Preserves challenge compatibility |
| Product JSON ranking | Implemented | `rank.py`, `io.build_product_ranking_output` | `--output` writes metadata, role requirements, rankings, ledgers | `outputs/ranked_candidates.json` | Rich submission/demo artifact |
| Product CSV | Implemented | `io.write_product_csv` | Writes normalized score columns and review tag | `outputs/ranked_candidates.csv` | Spreadsheet-friendly |
| JD matrix | Implemented, heuristic | `job_understanding.py`, `RoleRequirementMatrix` | Regex/label extraction, no LLM | Dashboard/run-ranking/detail | Shows hiring intent |
| JD-aware scoring | Implemented, partial | `scoring.apply_role_requirements_adjustments` | Boosts must-have/good/strong signal matches and adjusts seniority/location/availability/blockers | Product rank command | Better than fixed scoring, but heuristic |
| Candidate ingestion | Implemented | `schema.load_candidate_records` | Reads JSONL, GZIP JSONL, JSON, CSV | CLI/API upload | Handles common data formats |
| Data quality report | Implemented | `schema.load_candidate_records`, `rank.py` | Writes assumptions, malformed rows, coverage | `outputs/data_quality_report.json` | Input transparency |
| Feature extraction | Implemented | `features.extract_features` | Extracts deterministic signals from profile, skills, career, Redrob signals | All rankings | Core ranking logic |
| Evidence ledger | Implemented | `evidence_ledger.py` | Builds positive/negative/missing evidence with snippets/source fields | Candidate detail + JSON | Audit trail |
| Claim/proof labels | Implemented | `evidence_ledger._evidence_item` | Labels skill/profile as claim; career/production as proof/strong proof | Evidence Ledger UI | Prevents overclaiming |
| Risk radar | Implemented | `risk.build_risk_radar` | Maps risk flags to severity/evidence/impact/explanation | UI + JSON | Shows concerns |
| Review tags | Implemented | `review_tags.py` | Deterministic “why not higher” tags from scores, risks, missing evidence | Candidate table/detail | Fast recruiter triage |
| Trust audit | Implemented | `trust_audit.py`, `/api/trust-audit`, `frontend/app/trust-audit` | Summarizes latest payload counts/distributions | Trust Audit page | Builds judge trust |
| Battle cards | Implemented | `battlecards.py`, `src/redrob_ranker/battlecards.py` | Markdown summary from ranking JSON | `outputs/battlecards.md` | Recruiter-ready explanation |
| Candidate comparison | Implemented | `comparison.py`, `compare.py`, `/api/compare`, `frontend/app/compare` | Compares scores/evidence/risks | Compare page/CLI | Explains A vs B |
| Evaluation | Implemented | `evaluation.py`, `evaluate.py` | Uses labels if provided; proxy if not | `outputs/evaluation_report.md` | Honest metrics |
| Runtime benchmark | Implemented | `scripts/benchmark_runtime.py` | Duplicates records with unique IDs and times scoring | `outputs/performance_report.md` | Runtime proof |
| Responsible ranking guard | Implemented, limited | `fairness.py`, `scoring.score_candidate` | Strips configured protected attributes | Metadata/docs/tests | Role-relevance guard |
| FastAPI backend | Implemented | `api/main.py`, `api/routes/*`, `api/services/ranker_service.py` | HTTP wrapper around same engine | Backend demo | Product surface |
| Multipart upload | Implemented | `api/routes/ranking.py`, `RankerService.rank_uploaded_candidates` | Upload candidate file + job text/file | Run Ranking page/API tests | Realistic demo upload |
| Frontend console | Implemented | `frontend/app/*`, components, hooks, API client | Next.js pages fetch latest ranking or demo fallback | Browser | Judge-facing product |
| Demo fallback warning | Implemented | `frontend/lib/api.ts`, `useRankingData`, `run-ranking/page.tsx` | Falls back to `demoPayload` with visible warning when live ranking fails | UI | Avoids silent fake behavior |
| Intentional demo mode | Implemented | `frontend/app/run-ranking/page.tsx` | `Use Demo Scenario` loads demo payload intentionally | Run Ranking page | Safe demo path |

## 6. What is missing or partial

| Feature or expectation | Status | Reason | Impact | Suggested fix |
|---|---|---|---|---|
| Real recruiter accuracy | Missing | No real labels in repo except example labels | Cannot claim real accuracy | Run labeled evaluation on official labels |
| LLM semantic JD parser | Not implemented | Project intentionally uses deterministic heuristics | Do not claim LLM understanding | Add optional local/LLM parser only if allowed |
| Persistent run storage | Missing | Backend stores latest payload in memory | Runs disappear on restart | Add database or file-backed run store |
| Production large-file upload | Partial | Multipart uploads are buffered/temp-file based | Large 487 MB uploads may need hardening | Streaming object storage + background jobs |
| Auth/user accounts | Missing | Hackathon local demo only | Not production SaaS ready | Add auth/session model |
| Frontend exhaustive error states | Partial | Core errors/fallback exist, not exhaustive | Some failures are simple messages | Add structured toasts/status panels |
| Trust audit history | Missing | Trust audit derives latest in-memory payload | No trend/audit history | Persist runs and audit snapshots |
| Bias/fairness measurement | Partial | Protected attributes stripped, no statistical bias eval | Cannot claim fairness certification | Add bias metrics on labeled data |
| Learning-to-rank | Missing | Rule/evidence scoring only | No learned calibration | Add training when labels exist |
| Hosted public demo | Missing | Local only | Judges must run locally | Deploy backend/frontend |

## 7. User workflow

1. Recruiter opens the console at `/dashboard`.
2. Recruiter inputs or uploads a JD on `/run-ranking`.
3. Recruiter uploads/pastes candidate JSON/JSONL/CSV data.
4. System extracts a deterministic JD requirement matrix.
5. System normalizes candidate data through `CandidateRecord`.
6. System scores candidates with `score_candidates` and `rank_scored_candidates`.
7. System generates evidence ledgers with source snippets and claim/proof labels.
8. System shows risk radar and review tags.
9. Recruiter compares two candidates in `/compare`.
10. Recruiter exports JSON/CSV/battle cards/evaluation/performance artifacts.

## 8. Old challenge workflow

Command:

```powershell
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv --top-n 3
```

Output columns:

```text
candidate_id,rank,score,reasoning
```

Validation:

```powershell
python validate.py outputs/submission.csv --expected-rows 3
```

Verified result: `Submission is structurally valid: outputs\submission.csv`.

## 9. Product workflow

Command:

```powershell
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
```

Important output files:

- `outputs/ranked_candidates.json`
- `outputs/ranked_candidates.csv`
- `outputs/evidence_ledgers.json`
- `outputs/data_quality_report.json`
- `outputs/runtime_summary.json`
- `outputs/top_candidates_audit.csv`

Main UI routes:

- `/dashboard`
- `/run-ranking`
- `/candidates`
- `/candidates/[id]`
- `/compare`
- `/trust-audit`
- `/evaluation`
- `/exports`

## 10. Best demo flow

| Step | What to click | What to show | What to say | Why it matters |
|---|---|---|---|---|
| 1 | Open `/dashboard` | KPI cards and JD Understanding | “This is deterministic JD matrix extraction, not LLM parsing.” | Sets truthful scope |
| 2 | Open `/run-ranking` | Upload/paste area | “The same engine supports CLI and API upload.” | Shows workflow |
| 3 | Click `Use Demo Scenario` | Demo scenario status | “This is intentional demo mode; fallback is separate.” | Trust |
| 4 | Open candidate table | Review Tag column | “Recruiters immediately see why to review.” | Triage |
| 5 | Open `CAND_DEMO_001` | Scores/reasoning | “The top candidate has career-backed proof.” | Proof over claims |
| 6 | Show Evidence Ledger tabs | Source/snippet/claim/proof | “Every item has a field and snippet.” | No hallucination |
| 7 | Show Risk Radar | Risks and missing evidence | “Ranking includes concerns, not just positives.” | Real judgment |
| 8 | Open `/compare` | A/B comparison | “Backend decides evidence differences.” | Decision support |
| 9 | Open `/trust-audit` | Missing/risk/proof counts | “Limitations are visible.” | Judge trust |
| 10 | Open `/exports` | JSON/CSV endpoints | “Outputs are submission/demo ready.” | Deliverables |

## 11. Strongest winning points

1. Preserves old Redrob CSV submission command.
2. Adds product-grade JSON with metadata, JD matrix, scores, reasons, risks, and ledgers.
3. Separates candidate claims from proof with source snippets.
4. Scores fit, proof, confidence, hireability, and risk.
5. Provides review tags and “why not higher” signals.
6. Exposes Trust Audit instead of hiding limitations.
7. Supports JSONL, JSONL.GZ, JSON, CSV, and multipart upload.
8. Has backend candidate comparison and frontend compare page.
9. Runs locally without paid APIs or LLM calls.
10. Has 81 passing tests and a passing Next.js build.

## 12. Honest limitations

| Current limitation | Why it matters | How to explain it honestly | Future improvement |
|---|---|---|---|
| No real labels in repo | Cannot claim recruiter accuracy | “Metrics are proxy unless labels are supplied.” | Add official labels |
| JD parsing is heuristic | Could miss nuanced JD requirements | “Deterministic matrix extraction, not LLM parsing.” | Better parser/configurable profiles |
| In-memory backend state | Latest run is not durable | “Local demo state only.” | Database/file-backed runs |
| Large uploads buffered | Full 487 MB production upload may need hardening | “Multipart works but needs streaming for production.” | Streaming/background jobs |
| Risk rules are deterministic | May miss subtle profile risks | “Risk radar is explicit but not exhaustive.” | Broader taxonomy/calibration |
| Frontend local only | No public hosted demo | “Run locally from README.” | Deploy |
| No authentication | Not multi-user production SaaS | “Hackathon demo surface.” | Auth/session management |
