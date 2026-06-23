# Evaluation

Evaluation supports two modes.

## Mode 1: Labels Supplied

When labels are supplied, `evaluate.py` calculates:

- Precision@K,
- Recall@K,
- NDCG@K,
- MRR,
- false positives,
- false negatives.

Example:

```powershell
python evaluate.py --ranking outputs/ranked_candidates.json --labels data/labels.example.json --output outputs/evaluation_report.md --top-n 4
```

These metrics are labeled as real only because labels were supplied by the caller.

## Mode 2: No Labels

Without labels, evaluation is proxy-only:

- high-risk profiles in top K,
- strong-proof profiles in top K,
- profiles with missing evidence in top K,
- deterministic sort check.

Example:

```powershell
python evaluate.py --ranking outputs/ranked_candidates.json --output outputs/evaluation_report.md --top-n 4
```

Proxy metrics are not real recruiter accuracy.

## Synthetic Evaluation

The existing `scripts/synthetic_evaluation.py` remains available for archetype testing, including keyword stuffing, negation, missing metadata, outside-India logistics, proof-versus-keyword behavior, and deterministic ties.
