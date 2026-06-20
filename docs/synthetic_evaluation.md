# Synthetic Ranking Evaluation

## Purpose

Unit tests verify individual scoring behaviors, but they do not show whether the complete ranker creates a sensible shortlist. This evaluation generates a labeled candidate pool and measures the final ordering.

Synthetic results are a regression and stress test, not a substitute for evaluation on the private challenge dataset.

## Candidate pool

The default run creates 300 candidates across 12 archetypes, 25 candidates each:

| Archetype | Expected behavior |
|---|---|
| Strong production search/ranking engineer | Shortlist |
| Strong plain-language relevance engineer | Shortlist |
| Strong fit with missing behavioral telemetry | Shortlist |
| Strong fit but stale, unresponsive, and unavailable | Below ready candidates |
| Strong overseas fit, unwilling to relocate | Below India-ready candidates |
| Profile-only search/ranking claims | Below career-backed evidence |
| Junior retrieval engineer | Below senior candidates |
| Backend/platform engineer without model ownership | Adjacent, not shortlist |
| Computer-vision/speech specialist transitioning domains | Down-ranked |
| Negated search/ranking claims | Must not count as evidence |
| Generic LLM/RAG demos and tutorials | Strongly down-ranked |
| Non-technical keyword stuffing | Bottom-ranked |

The generator randomizes experience, titles, employers, industries, impact values, and some profile attributes using a fixed seed.

## Results

Command:

```powershell
python scripts/synthetic_evaluation.py --per-archetype 25 --top-n 75
```

Verified result for seed `20260617`:

- Candidates: 300
- Intended shortlist candidates: 75
- Precision@75: **1.000**
- Recall@75: **1.000**
- NDCG@75: **0.979**
- False positives: **0**
- False negatives: **0**

The top 75 consisted only of strong production search/ranking engineers, strong plain-language relevance engineers, and strong fits with missing telemetry. Profile-only claims, junior candidates, unrelated ML profiles, negated claims, generic demos, and keyword stuffing stayed below the shortlist boundary.

Five additional seeds (`11`, `29`, `101`, `777`, and `2026`) produced the same 1.000 precision and recall with NDCG@60 of 0.978.

A larger run with 1,200 candidates (100 per archetype) also produced Precision@300 and Recall@300 of 1.000, with NDCG@300 of 0.983.

## Calibration discovered by the test

The first run produced precision and recall of 0.667 because strong overseas candidates explicitly unwilling to relocate outranked India-based plain-language matches. The logistics penalty was then split:

- Smaller penalty when an overseas candidate is willing to relocate.
- Material penalty when the candidate is unwilling to relocate.

After recalibration, all intended shortlist candidates cleared the boundary across the tested seeds.

## Artifacts

Each run writes:

- `.synthetic-eval/metrics.json`
- `.synthetic-eval/ranking.csv`

Generated artifacts are ignored by Git. The lightweight regression version runs as part of the normal test suite.
