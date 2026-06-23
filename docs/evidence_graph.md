# Evidence Graph

The Evidence Ledger is the product form of the ranker's evidence graph. Each ranked candidate receives:

- positive evidence,
- negative evidence,
- missing evidence,
- risk flags,
- source fields,
- score impacts,
- interview focus,
- grounded explanation.

## Evidence Item Shape

Each evidence item includes:

- `evidence_type`
- `concept`
- `source_field`
- `snippet`
- `strength`
- `confidence`
- `polarity`
- `claim_or_proof`
- `score_impact`

## Claim And Proof Separation

Skill lists and profile summaries are treated as claims. Career-history descriptions are treated as proof when they mention role-relevant work. Production terms such as shipped, deployed, serving, launched, and owned strengthen proof.

The system does not invent snippets. If supplied fields are insufficient, missing evidence is listed explicitly.
