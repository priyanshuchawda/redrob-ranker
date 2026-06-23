# Redrob Track 1 Submission

## Team Name

AllKnighters

## Product

EvidenceGraph Ranker is now both a preserved challenge ranker and a runnable recruiting intelligence product. The product positioning is:

> Most hiring tools improve resume search. EvidenceGraph Ranker improves hiring judgment.

It ranks candidates by role fit, proof strength, confidence, hireability, and risk, not by resume keyword overlap.

## Original Challenge Compatibility

The original command still works:

```powershell
python rank.py --candidates candidates.jsonl --out submission.csv
```

The CSV contract is unchanged:

```text
candidate_id,rank,score,reasoning
```

The existing deterministic engine, debug CSV, audit CSV, validation, and tests were kept.

## Product Workflow

```powershell
python rank.py --job data/job.txt --candidates data/candidates.jsonl --output outputs/ranked_candidates.json --csv-out outputs/ranked_candidates.csv --top-n 50 --audit
python battlecards.py --ranking outputs/ranked_candidates.json --output outputs/battlecards.md --top-n 10
python compare.py --job data/job.txt --candidates data/candidates.jsonl --a CAND_DEMO_001 --b CAND_DEMO_002
python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
```

## What Was Added

- JD understanding with `RoleRequirementMatrix`.
- JD-aware scoring adjustments on top of the calibrated scoring engine.
- Flexible ingestion for JSONL, JSONL.GZ, JSON, CSV, and nested candidate records.
- Data quality reporting.
- Product JSON and CSV outputs.
- Evidence Ledger separating claims from proof.
- Structured Risk Radar.
- Rich deterministic recruiter reasoning.
- Battle cards.
- Candidate comparison.
- Responsible ranking guard and documentation.
- FastAPI backend.
- Next.js Recruiter Intelligence Console.
- Labeled/proxy evaluation flow with honest labels.

## Explainability

All explanations are grounded in supplied candidate fields. The system can say evidence is unclear, but it does not invent candidate facts.

## Responsible Ranking

The scoring path ignores protected and irrelevant personal attributes such as gender, religion, caste, race, marital status, political views, disability, unrelated personal details, and age. Product JSON includes:

```json
{
  "ranking_uses_role_relevant_evidence_only": true
}
```

## Verification

Current local verification:

- `python -m pytest -q`: 67 passed.
- Old challenge CSV command: passed on demo data.
- Local CSV validator: passed on demo output.
- Product JD ranking command: passed.
- Battle cards: generated.
- Candidate comparison: generated.
- Proxy evaluation: generated and labeled as proxy.
- FastAPI app import and test-client health/rank smoke test: passed.
- Frontend `npm install`: completed after an initial timeout left partial dependencies.
- Frontend `npm run build`: passed.

## Evaluation Note

When labels exist, `evaluate.py` can calculate Precision@K, Recall@K, NDCG@K, MRR, false positives, and false negatives. Without labels, it reports proxy checks only and does not claim real recruiter accuracy.

## Final Submission Fields Still Needed

- Primary contact name, email, and phone.
- Full team member list.
- Public demo or deployment link, if required by the portal.
