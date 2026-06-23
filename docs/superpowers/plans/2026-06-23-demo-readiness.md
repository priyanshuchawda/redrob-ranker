# Demo Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the judge-facing UI to real comparison and upload APIs while making degraded demo behavior explicit and product claims factual.

**Architecture:** Preserve the existing JSON ranking route and service. Add a thin multipart adapter that feeds the existing ingestion and ranking pipeline, then update client API types and pages to render backend-owned decisions.

**Tech Stack:** Python, FastAPI, Pydantic, pytest, Next.js 14, React, TypeScript, Tailwind CSS.

---

### Task 1: Multipart Ranking Adapter

**Files:**
- Modify: `requirements.txt`
- Modify: `api/routes/ranking.py`
- Modify: `api/services/ranker_service.py`
- Test: `tests/test_api_backend.py`

- [ ] Add a failing API test that posts a JD and JSONL candidate file to `/api/rank/upload`, then asserts a successful product ranking response.
- [ ] Run `python -m pytest tests/test_api_backend.py -q` and confirm the new test fails because the route does not exist.
- [ ] Add a failing malformed-upload test expecting HTTP 400 and a useful detail.
- [ ] Implement upload parsing with `UploadFile`, `Form`, and the existing `load_candidate_records` adapter through a temporary file.
- [ ] Add `python-multipart` to runtime requirements.
- [ ] Run `python -m pytest tests/test_api_backend.py -q` and confirm both upload tests pass.

### Task 2: Backend-Owned Comparison UI

**Files:**
- Modify: `frontend/lib/types.ts`
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/app/compare/page.tsx`

- [ ] Define `ComparisonPayload`, candidate summary, evidence difference, and risk types matching `/api/compare`.
- [ ] Make `compareCandidates` return `Promise<ComparisonPayload>` and preserve backend error details.
- [ ] Replace local score-delta logic with an explicit compare action, loading state, error state, and backend response rendering.
- [ ] Render why A ranks above B, where B is stronger, component differences, evidence differences, risks for both candidates, and what to verify.
- [ ] Run `npm run build` and confirm TypeScript and Next.js compilation pass.

### Task 3: Explicit Fallback State and File Upload

**Files:**
- Modify: `frontend/lib/api.ts`
- Modify: `frontend/app/run-ranking/page.tsx`

- [ ] Add a multipart client helper for `/api/rank/upload`.
- [ ] Track the selected candidate file separately from pasted text.
- [ ] Use multipart upload for selected files and the existing JSON route for pasted candidate text.
- [ ] On failure, render a persistent warning panel containing exactly `Live ranking failed. Showing demo fallback.`
- [ ] Keep the bundled demo payload available so the demo remains navigable.
- [ ] Run `npm run build` and confirm the page compiles.

### Task 4: Factual Documentation

**Files:**
- Modify: `README.md`
- Modify: `FINAL_REPORT.md`
- Modify: `FINAL_TECHNICAL_AUDIT.md`

- [ ] Replace the multipart limitation with the implemented endpoint and supported formats.
- [ ] Describe JD processing as deterministic JD requirement matrix extraction.
- [ ] List only Next.js, TypeScript, Tailwind CSS, FastAPI, and Python for the product stack.
- [ ] Record the comparison page as backend-integrated and the fallback warning as explicit.

### Task 5: Verification and Delivery

**Files:**
- Modify only if verification finds defects.

- [ ] Run `python -m pytest -q`.
- [ ] Run `npm run build` in `frontend/`.
- [ ] Start FastAPI and Next.js, then verify live comparison and fallback behavior in a browser.
- [ ] Review `git diff --check` and the scoped diff.
- [ ] Commit, push, open a ready PR, merge it, delete the branch locally and remotely, and confirm GitHub exposes only `main`.
