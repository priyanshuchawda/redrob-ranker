# Redrob Ranker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic CLI ranker that produces a valid, explainable top-100 candidate CSV for the Redrob Senior AI Engineer JD.

**Architecture:** A small Python package streams candidate records, extracts JD-specific features, scores each candidate, keeps the best rows, generates grounded reasoning, and writes validator-compatible CSV. The CLI has no network calls and no dashboard.

**Tech Stack:** Python standard library plus pytest for tests.

---

## File Structure

- `rank.py`: CLI entrypoint.
- `src/redrob_ranker/models.py`: typed dataclasses for scoring features and ranked rows.
- `src/redrob_ranker/features.py`: candidate text normalization and feature extraction.
- `src/redrob_ranker/scoring.py`: deterministic scoring, risk penalties, and ranking.
- `src/redrob_ranker/reasoning.py`: factual reasoning generator.
- `src/redrob_ranker/io.py`: JSONL/GZIP loading and CSV writing.
- `tests/test_features.py`: feature extraction tests.
- `tests/test_scoring.py`: scoring and ordering tests.
- `tests/test_io.py`: CSV output tests.
- `tests/fixtures.py`: small in-memory candidate fixtures.

## Tasks

### Task 1: Feature Extraction

**Files:**
- Create: `src/redrob_ranker/models.py`
- Create: `src/redrob_ranker/features.py`
- Create: `tests/fixtures.py`
- Create: `tests/test_features.py`

- [ ] Write tests proving retrieval/ranking/product/availability features are extracted from candidate records.
- [ ] Run `python -m pytest tests/test_features.py -q` and confirm tests fail because extraction code is missing.
- [ ] Implement the minimal feature extractor.
- [ ] Re-run the feature tests and confirm they pass.

### Task 2: Scoring

**Files:**
- Create: `src/redrob_ranker/scoring.py`
- Create: `tests/test_scoring.py`

- [ ] Write tests showing a true applied ML/retrieval candidate outranks a keyword-stuffed non-ML candidate.
- [ ] Write tests showing stale/low-response availability reduces score.
- [ ] Run `python -m pytest tests/test_scoring.py -q` and confirm tests fail.
- [ ] Implement deterministic scoring and ranking.
- [ ] Re-run scoring tests and confirm they pass.

### Task 3: Reasoning

**Files:**
- Create: `src/redrob_ranker/reasoning.py`
- Modify: `tests/test_scoring.py`

- [ ] Write tests showing reasoning includes factual strengths and concern language.
- [ ] Run the tests and confirm they fail.
- [ ] Implement grounded reasoning from candidate fields and extracted features.
- [ ] Re-run tests and confirm they pass.

### Task 4: I/O and CLI

**Files:**
- Create: `src/redrob_ranker/io.py`
- Create: `rank.py`
- Create: `tests/test_io.py`

- [ ] Write tests for JSONL loading, CSV writing, rank assignment, score monotonicity, and candidate-id tie-breaks.
- [ ] Run I/O tests and confirm they fail.
- [ ] Implement loading, output writing, and CLI argument handling.
- [ ] Re-run all tests and confirm they pass.

### Task 5: Full Dataset Run

**Files:**
- Modify: `README.md`

- [ ] Run `python rank.py --candidates "<bundle>/candidates.jsonl" --out submission.csv`.
- [ ] Run the provided `validate_submission.py submission.csv`.
- [ ] Inspect the top and bottom of the top 100 for obvious false positives.
- [ ] Record runtime and methodology details in README.

