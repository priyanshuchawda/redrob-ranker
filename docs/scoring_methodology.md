# Scoring Methodology

## Objective

Rank candidates for a Senior AI Engineer role whose highest-value work is production retrieval, matching, recommendation, ranking, and evaluation. The system optimizes for evidence quality and recruiter trust rather than raw keyword frequency.

## Evidence graph

The feature extractor maps phrases and structured fields into concepts instead of independently rewarding every synonym. For example, `semantic search`, `hybrid search`, and `vector search` contribute to one retrieval concept within a job entry. This limits score inflation from repeated or overlapping terms.

Concept families:

1. **Retrieval:** semantic/vector search, dense representations, retrieval infrastructure, matching, candidate generation, search relevance, and dual-encoder retrieval.
2. **Ranking:** learning-to-rank, reranking, recommendation systems, ranking systems, matching policies, and ranking heuristics.
3. **Evaluation:** ranking metrics, offline evaluation, online experiments, relevance quality, product outcomes, and evaluation methodology.

Current roles receive full evidence weight. Older roles receive a gradually lower weight. Production context gives an evidence item a small trust boost.

## Evidence quality

The ranker separates four ideas that keyword filters usually collapse:

- **Mention:** the concept appears in career history.
- **Ownership:** language such as owned, led, designed, architected, or built.
- **Production:** shipped, deployed, serving, launched, scaled, or operationalized.
- **Impact:** measurable improvements, reductions, growth, latency, percentages, or scale.

Negated clauses such as “no production retrieval or ranking ownership” are not counted as positive evidence.

## Skill trust and corroboration

Skills are normalized case-insensitively with aliases such as `cross-encoder`, `learning-to-rank`, and `vector-search`.

A skill gains trust from:

- Duration.
- Proficiency.
- Endorsements.
- Assessment score.
- Supporting career evidence.

Short-duration buzzword clusters lose trust. Multiple “expert” skills with zero duration trigger a keyword-stuffing risk. Corroboration is awarded only when a skill family and corresponding career evidence both exist.

## Practical hireability

Availability uses open-to-work status, recency, recruiter response rate, response time, notice period, recruiter saves, interview completion, offer acceptance, and verification.

Logistics uses country, target cities, relocation willingness, and preferred work mode. Missing behavioral fields are unknown rather than negative. Rates in either `0-1` or `0-100` form are normalized.

These components are deliberately weighted below core fit. A highly responsive candidate without production relevance should not outrank a strong applied ML engineer.

## Risk controls

Material penalties cover:

- Keyword-stuffed profiles.
- Generic LLM/RAG demos without shipped retrieval evidence.
- Computer-vision, speech, or robotics pivots without target-domain depth.
- Outside-India logistics.
- Stale activity and low recruiter response.
- Long notice periods.
- Service-company and consulting-only indicators.
- Major inconsistencies between stated experience and career history.
- Insufficient career evidence.

## Ranking and explanations

Component weights are centralized in `src/redrob_ranker/config.py`. Features are bounded before weighting so a single field cannot grow without limit.

Final ordering is:

1. Total score descending.
2. `candidate_id` ascending for deterministic ties.

The explanation generator uses only profile fields and extracted evidence. It includes concrete role, experience, evidence, location, response, notice, and concern facts when those fields are available.

## Complexity

For `N` candidates and a fixed concept vocabulary, feature extraction and scoring are `O(N)`. Ranking is `O(N log N)` with the current full audit-friendly implementation. Memory is `O(N)` because optional debugging and auditing require component records for every candidate; 100,000 records remain comfortably inside the challenge's 16 GB limit.
