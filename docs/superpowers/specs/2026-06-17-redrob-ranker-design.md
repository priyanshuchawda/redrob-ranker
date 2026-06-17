# Redrob Candidate Ranker Design

## Goal

Build a reproducible CLI ranker that reads the 100,000-candidate JSONL pool and writes a valid top-100 CSV for the Senior AI Engineer founding-team JD.

## Constraints

- CPU-only ranking.
- No network calls during ranking.
- Complete within 5 minutes and 16 GB RAM.
- Output exactly `candidate_id,rank,score,reasoning`.
- Scores must be non-increasing by rank.
- Reasoning must be factual, candidate-specific, and tied to the JD.
- Avoid dashboards and unnecessary UI.

## Ranking Approach

Use a deterministic hybrid scorer:

- Core evidence score from current title, career-history titles, career descriptions, and skills.
- Seniority score for the target 5-9 year band, with room for very strong outliers.
- Production/product score for product-company and shipped-system evidence.
- Retrieval/ranking score for embeddings, vector search, recommendation systems, search, ranking, evaluation, and A/B testing.
- Logistics score for India, Pune/Noida or nearby tier-1 cities, relocation, work mode, notice period, and salary reasonableness.
- Availability score from open-to-work, recent activity, recruiter response rate, response time, interview completion, offer acceptance, recruiter saves, and verification signals.
- Risk penalties for keyword stuffing, suspicious skill-duration claims, service-only trajectories, stale/low-response profiles, and possible honeypot anomalies.

## Output Reasoning

Reasoning is assembled from scored features and source fields. It should mention concrete evidence such as current title, years of experience, relevant career-history evidence, location, open-to-work, response rate, notice period, and concern flags. The generator must not invent employers, skills, or model names.

## Testing

Tests cover:

- Candidate parsing and feature extraction.
- JD evidence detection from profile, skills, and career history.
- Behavioral scoring and risk penalties.
- Deterministic top-100 ordering and tie-breaking.
- CSV shape and validator-compatible output.
- Reasoning grounded in available candidate facts.

## Submission Package

The repo will contain source code, tests, README instructions, metadata template, and generated diagrams if useful for the final write-up. The raw challenge dataset is excluded from Git.

