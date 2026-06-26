# PPT Source Notes

## Slide 1: Title

- Slide title: EvidenceGraph Ranker
- Headline: Candidate ranking by evidence, not keyword overlap.
- Bullets:
  - Redrob candidate ranking challenge
  - Deterministic Python + FastAPI + Next.js product
  - JD matrix, evidence ledger, risk radar, comparison, trust audit
  - No paid APIs or LLM calls required
- Suggested visual: JD + candidates flowing into ranked shortlist.
- Speaker line: “This project helps recruiters judge proof, confidence, hireability, and risk.”
- Exact facts: `rank.py`, `src/redrob_ranker`, `api`, `frontend`, 81 passing tests.
- Do not overclaim: Do not say real recruiter accuracy or LLM semantic parsing.

## Slide 2: Solution Overview

- Slide title: Solution Overview
- Headline: JD in, evidence-backed shortlist out.
- Bullets:
  - Parses JD into deterministic `RoleRequirementMatrix`
  - Loads JSONL, JSONL.GZ, JSON, CSV, and multipart uploads
  - Scores candidates with evidence, proof, risk, and hireability
  - Exports CSV/JSON/evidence/battle-card outputs
- Suggested visual: pipeline with four stages.
- Speaker line: “The system is not just a table of scores; it gives an audit trail.”
- Exact facts: `job_understanding.py`, `schema.py`, `scoring.py`, `io.py`.
- Do not overclaim: Do not call ingestion streaming production-grade for huge files.

## Slide 3: JD Understanding and Candidate Evaluation

- Slide title: JD Understanding and Candidate Evaluation
- Headline: A visible requirement matrix keeps ranking intent inspectable.
- Bullets:
  - Extracts role title, must-have skills, strong signals, good-to-have skills
  - Extracts seniority, domain, production, leadership, location, availability, blockers
  - Candidate features include career, profile, skills, production, availability, logistics
  - JD-aware scoring is deterministic and heuristic
- Suggested visual: JD matrix card screenshot.
- Speaker line: “Judges can see what the system thinks the job asks for.”
- Exact facts: `RoleRequirementMatrix`, `RoleRequirementMatrix.tsx`.
- Do not overclaim: Do not say the JD parser understands arbitrary nuance like an LLM.

## Slide 4: Ranking Methodology

- Slide title: Ranking Methodology
- Headline: Ranking combines fit, proof, confidence, hireability, and risk.
- Bullets:
  - Internal components: role, seniority, retrieval, ranking, evaluation, profile evidence, skills, product, production, engineering, leadership, confidence, availability, logistics, risk
  - Product scores: final, fit, proof, confidence, hireability, risk
  - JD adjustments reward must-have and strong-signal matches
  - Stable tie-break: score descending, candidate ID ascending
- Suggested visual: score component stack.
- Speaker line: “A candidate cannot win by keywords alone if proof and hireability are weak.”
- Exact facts: `score_components`, `normalize_product_scores`, `apply_role_requirements_adjustments`.
- Do not overclaim: Do not say scoring is trained; it is deterministic.

## Slide 5: Explainability and Data Validation

- Slide title: Explainability and Data Validation
- Headline: Every shortlist decision has evidence and checks.
- Bullets:
  - Evidence ledger shows source field, snippet, claim/proof label, confidence, score impact
  - Risk radar surfaces concerns
  - Missing evidence and interview focus guide recruiter review
  - Validator preserves legacy CSV structure
- Suggested visual: evidence ledger panel.
- Speaker line: “If evidence is missing, the system says missing instead of inventing it.”
- Exact facts: `evidence_ledger.py`, `risk.py`, `validation.py`, `EvidenceLedgerPanel.tsx`.
- Do not overclaim: Do not say the system verifies truth outside the supplied profile.

## Slide 6: End to End Workflow

- Slide title: End to End Workflow
- Headline: One local workflow supports challenge submission and product demo.
- Bullets:
  - Old path: `rank.py --out submission.csv`
  - Product path: `rank.py --job ... --output ranked_candidates.json`
  - Backend: `uvicorn api.main:app --reload`
  - Frontend: `npm run dev`
- Suggested visual: CLI/API/UI swimlane.
- Speaker line: “The old challenge workflow remains intact while the product workflow adds explainability.”
- Exact facts: README commands and verified outputs.
- Do not overclaim: Do not say deployed unless hosted.

## Slide 7: System Architecture

- Slide title: System Architecture
- Headline: Core engine is separated from API and UI.
- Bullets:
  - `src/redrob_ranker` owns business logic
  - `api` wraps the engine with FastAPI endpoints
  - `frontend` consumes latest ranking, upload, compare, and trust-audit APIs
  - CLI tools use the same engine
- Suggested visual: Mermaid architecture diagram from `ARCHITECTURE_DEEP_DIVE.md`.
- Speaker line: “There is one ranking engine, not separate demo logic.”
- Exact facts: `api/services/ranker_service.py`, `frontend/lib/api.ts`.
- Do not overclaim: Demo fallback exists; it is separate and visible.

## Slide 8: Results and Performance

- Slide title: Results and Performance
- Headline: Tested locally; metrics are honest and labeled.
- Bullets:
  - 81 Python tests passed
  - Next.js production build passed
  - Benchmark: 100 candidates in 0.221286s; 1000 in 1.607923s
  - Evaluation without labels is proxy only
- Suggested visual: test/build/benchmark cards.
- Speaker line: “The project reports proxy metrics only when labels are absent.”
- Exact facts: pytest output, `outputs/performance_report.md`, `outputs/evaluation_report.md`.
- Do not overclaim: Do not claim official accuracy.

## Slide 9: Technologies Used

- Slide title: Technologies Used
- Headline: Lightweight local stack, no paid inference dependency.
- Bullets:
  - Python deterministic ranking engine
  - FastAPI + python-multipart
  - Next.js 14, TypeScript, Tailwind CSS
  - Pytest test suite
- Suggested visual: stack diagram.
- Speaker line: “This runs locally from a fresh clone after installing dependencies.”
- Exact facts: `requirements.txt`, `frontend/package.json`.
- Do not overclaim: Do not list libraries not in package files.

## Slide 10: Submission Assets

- Slide title: Submission Assets
- Headline: Code, outputs, reports, and judge-facing docs are included.
- Bullets:
  - Legacy CSV: `outputs/submission.csv`
  - Product JSON/CSV and evidence ledgers
  - Battle cards, comparison JSON, evaluation and performance reports
  - README, final report, technical audit, deep-dive docs
- Suggested visual: folder/file checklist.
- Speaker line: “The repo includes both runnable code and explanatory artifacts.”
- Exact facts: `outputs/*`, docs created in this task.
- Do not overclaim: Output files are local generated artifacts, not official portal submission unless run on final dataset.

## Slide 11: Closing or Thank You

- Slide title: Thank You
- Headline: Evidence-based ranking makes shortlisting more inspectable.
- Bullets:
  - Proof over claims
  - Risk before shortlist
  - Hiring feasibility included
  - Recruiter knows what to verify next
- Suggested visual: top candidate card with evidence ledger.
- Speaker line: “This is a practical decision-support layer for recruiter judgment.”
- Exact facts: Evidence ledger, review tags, trust audit, comparison.
- Do not overclaim: The tool supports recruiters; it does not replace interviews or human judgment.
