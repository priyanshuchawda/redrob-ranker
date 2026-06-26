# Judge Q&A Bank

## 1. What is this project?

EvidenceGraph Ranker is a proof-of-concept recruiting ranker for the Redrob candidate ranking challenge. It takes a job description and candidate records, ranks candidates, and produces recruiter-facing explanations: score breakdowns, evidence ledgers, risk radar, review tags, comparison output, battle cards, and exports.

## 2. What makes it different from keyword search?

It does not only count matching terms. The system separates claims from proof. A skill listed in a profile is treated differently from career-backed evidence in work history, projects, production ownership, ranking/retrieval work, evaluation work, and availability signals.

## 3. Is this an LLM product?

No. The current implementation is deterministic Python logic. It does not call OpenAI, paid APIs, or external model services. The job parser and scoring engine are heuristic and inspectable.

## 4. Why not use an LLM?

For this proof of concept, deterministic logic makes the ranking transparent, reproducible, fast, and easy to audit locally. A future version could add an optional LLM parser or embedding layer, but the current repo should not be presented as LLM-based.

## 5. How does the system understand the job description?

`src/redrob_ranker/job_understanding.py` parses the JD into a `RoleRequirementMatrix`. It extracts fields such as role title, must-have skills, strong signals, good-to-have skills, seniority, domain, production expectations, leadership expectations, location, availability, and risk blockers.

## 6. Is the JD understanding semantic?

Partially. It is deterministic and field/phrase-based, not learned semantic understanding. It is more structured than raw keyword matching, but it should not be described as full natural-language understanding.

## 7. What candidate data formats are supported?

The ingestion layer supports JSONL, JSONL.GZ, JSON, CSV, nested candidate payloads, and FastAPI multipart uploads. This is implemented in `src/redrob_ranker/schema.py` and wrapped by CLI/API flows.

## 8. What is the main scoring idea?

The scorer combines role fit, seniority, retrieval/search evidence, ranking evidence, evaluation evidence, profile evidence, skill trust, product sense, production proof, engineering depth, leadership, confidence, availability, logistics, and risk penalties.

## 9. What are the product score dimensions?

The product output includes final score, fit score, proof score, confidence score, hireability score, and risk score.

## 10. How is ranking deterministic?

The ranking uses fixed rules and weights. Ties are sorted by descending score and then ascending candidate ID. There is no randomness or external service dependency.

## 11. What is the Evidence Ledger?

The Evidence Ledger is an audit trail for each candidate. It lists positive evidence, negative evidence, missing evidence, source fields, snippets, claim/proof labels, confidence, approximate score impact, and interview focus.

## 12. What does claim versus proof mean?

A profile or skill field can be a claim. Career history, production context, and project descriptions can become proof or strong proof. The distinction helps avoid over-ranking keyword-stuffed profiles.

## 13. Does the system verify whether a candidate actually did the work?

No. It only uses supplied candidate fields. It does not externally verify employment history, projects, links, or claims. Missing or unclear proof is surfaced to the recruiter.

## 14. What is Risk Radar?

Risk Radar is a structured list of concerns such as weak proof, missing evidence, location mismatch, availability problems, generic AI demos, non-target domain signals, or other deterministic risk flags found in the supplied data.

## 15. Does risk affect ranking?

Yes. Risk contributes to scoring penalties and is also shown separately so recruiters can understand why a candidate may rank lower.

## 16. What are review tags?

Review tags are short recruiter-facing labels generated from score gaps, risks, and missing evidence. They summarize why a candidate needs closer review or why they did not rank higher.

## 17. What is Trust Audit?

Trust Audit summarizes the latest ranking payload: proof/claim patterns, risk counts, missing evidence categories, and other quality indicators. It exists to make limitations visible instead of hiding them.

## 18. What can the frontend show?

The frontend has pages for landing, dashboard, run ranking, candidates, candidate detail, compare, evaluation, exports, and trust audit. It is built with Next.js, React, TypeScript, and Tailwind CSS.

## 19. What can the backend do?

The FastAPI backend exposes health, demo data, ranking, latest ranking, upload ranking, candidate list/detail, comparison, evaluation, ranked JSON export, ranked CSV export, and trust audit endpoints.

## 20. What command creates the old challenge CSV?

```powershell
python rank.py --candidates data/candidates.jsonl --out outputs/submission.csv --top-n 3
```

The CSV is validated by:

```powershell
python validate.py outputs/submission.csv --expected-rows 3
```

## 21. What command creates the richer product output?

```powershell
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
```

## 22. What tests passed?

The verified Python test suite result was `81 passed in 2.45s` using the Windows Python 3.13 interpreter in this local environment.

## 23. Did the frontend build pass?

Yes. `npm run build` completed successfully in the `frontend` folder. The production build reported routes for `/`, `/candidates`, `/candidates/[id]`, `/compare`, `/dashboard`, `/evaluation`, `/exports`, `/run-ranking`, and `/trust-audit`.

## 24. Did the backend boot?

Yes. `uvicorn api.main:app --reload --host 127.0.0.1 --port 8020` booted successfully and reported the FastAPI application title as `EvidenceGraph Ranker API`.

## 25. Did the frontend dev server boot?

Yes. `npm.cmd run dev -- --hostname 127.0.0.1 --port 3020` booted the Next.js development server in this Windows environment.

## 26. What runtime benchmark was verified?

Using `scripts/benchmark_runtime.py` on duplicated demo candidates:

- 100 candidates: 0.221286 seconds, 451.9 candidates/second.
- 1000 candidates: 1.607923 seconds, 621.92 candidates/second.

These are local CPU benchmark numbers, not official production service-level objectives.

## 27. Are the evaluation metrics official?

No. If no labels are supplied, evaluation is proxy only. The repo has `data/labels.example.json`, but no official labeled benchmark is included. Do not claim real recruiter accuracy from proxy output.

## 28. What is the most honest accuracy statement?

The system is tested for structural correctness, deterministic ranking behavior, API behavior, ingestion behavior, UI source readiness, and proxy separation. Real ranking accuracy requires official labels or recruiter-reviewed ground truth.

## 29. Does this remove bias?

No. It includes a limited responsible-ranking guard that strips configured protected/irrelevant attributes before scoring, but this is not a statistical fairness audit and should not be described as bias-free hiring.

## 30. Can it handle the full challenge dataset?

It has flexible ingestion and linear deterministic scoring, but production-hard handling of very large files needs streaming/background-job hardening. Multipart upload works for the demo path; very large files should be tested and tuned before production.

## 31. Where is candidate comparison implemented?

Comparison is implemented in `src/redrob_ranker/comparison.py`, exposed by `compare.py`, wrapped by `/api/compare`, and used by `frontend/app/compare/page.tsx`.

## 32. Where are battle cards implemented?

Battle cards are implemented in `src/redrob_ranker/battlecards.py` and exposed by the root `battlecards.py` CLI.

## 33. What is the strongest demo path?

Open `/dashboard`, show the JD matrix, run intentional demo mode from `/run-ranking`, open `/candidates/CAND_DEMO_001`, show the Evidence Ledger and Risk Radar, compare `CAND_DEMO_001` against `CAND_DEMO_002`, then close with `/trust-audit` and `/exports`.

## 34. What should not be said in a demo?

Do not say:

- real recruiter accuracy was proven;
- the parser is LLM-based;
- the product is bias-free;
- uploaded evidence is externally verified;
- large-file upload is production-hardened;
- the system replaces recruiter judgment.

## 35. What is the best judge-facing framing?

This is a practical recruiter decision-support system. Its strongest contribution is not just ranking candidates, but showing evidence, gaps, risks, and verification prompts so the shortlist is inspectable.

## 36. What are the main limitations?

- No official labels in the repo.
- JD parsing is deterministic and heuristic.
- Backend latest-run state is in memory.
- No authentication or multi-tenant production model.
- Multipart upload is not a full production large-file pipeline.
- Fairness guard is limited and not a bias certification.
- The frontend is a local demo console, not a hosted SaaS deployment.

## 37. What would be the next upgrades?

1. Run official labeled evaluation.
2. Add persistent run storage.
3. Add streaming uploads and background jobs.
4. Add recruiter feedback and learning-to-rank calibration.
5. Add richer JD parsing.
6. Add statistical fairness evaluation.
7. Deploy a hosted backend/frontend demo.

