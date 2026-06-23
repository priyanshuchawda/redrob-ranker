# Scoring Methodology

EvidenceGraph Ranker keeps the original calibrated component scoring and adds normalized product scores for the UI and JSON output.

## Existing Component Scores

The original engine still computes:

- `role`
- `seniority`
- `retrieval`
- `ranking`
- `evaluation`
- `profile_evidence`
- `skills`
- `product`
- `production`
- `engineering`
- `leadership`
- `confidence`
- `availability`
- `logistics`
- `risk`
- `total`

These components preserve the challenge behavior and are still written to debug/audit outputs.

## JD-Aware Layer

When a job description is supplied, `job_understanding.py` creates a `RoleRequirementMatrix`. `scoring.py` then adjusts:

- skill relevance for must-have and good-to-have skills,
- semantic concept relevance for strong-signal phrases,
- seniority fit,
- production importance,
- domain fit,
- location fit,
- availability fit,
- blocker penalties.

If no JD is supplied, the original Senior AI Engineer calibration is used.

## Product Scores

Product-facing scores are normalized to 0-100 where practical:

- `final_score`: normalized total score.
- `fit_score`: role, seniority, core evidence, skills, and product fit.
- `proof_score`: career-backed retrieval/ranking/evaluation, production, and engineering evidence.
- `confidence_score`: evidence confidence component.
- `hireability_score`: availability, logistics, and leadership.
- `risk_score`: normalized risk pressure, where higher means more risk.

## Claim Versus Proof

The system rewards proof more than claims:

- Claim: candidate lists a skill or says a concept in profile text.
- Proof: work history describes using that concept in a project or role.
- Strong proof: work history includes production, shipped, deployed, owned, or serving context.

## Risk Controls

Risk penalties cover keyword stuffing, weak proof behind strong claims, generic AI demos, missing important evidence, stale activity, low response, long notice period, location mismatch, and non-target domain evidence.
