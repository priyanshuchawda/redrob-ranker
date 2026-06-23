# Responsible Ranking

EvidenceGraph Ranker is designed to rank role-relevant evidence, not protected or irrelevant personal attributes.

## What The System Uses

- Role title and seniority signals.
- Work history descriptions.
- Skills and skill corroboration.
- Production, engineering, evaluation, and leadership evidence.
- Availability and logistics signals relevant to recruiting feasibility.
- Risk flags derived from supplied candidate fields.
- Job description requirements supplied by the recruiter.

## What The System Ignores

The fairness guard removes or ignores:

- gender,
- religion,
- caste,
- race,
- marital status,
- political views,
- disability,
- unrelated personal details,
- age unless legally required, which this project does not assume.

Product output includes:

```json
{
  "ranking_uses_role_relevant_evidence_only": true
}
```

## Limitations

- The guard depends on recognizable field names and cannot guarantee that all biased language inside free text is removed.
- Location and availability are used only as role/logistics signals because the demo JD includes geography and timing constraints.
- The system is deterministic and transparent, but it still requires human review.

## Why This Improves Transparency

Recruiters can see which fields contributed evidence, which risks reduced confidence, and which missing evidence should be verified in interviews.
