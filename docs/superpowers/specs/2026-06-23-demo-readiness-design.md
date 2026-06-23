# Demo Readiness Design

## Goal

Make the final judge demo use real backend comparison and ranking behavior, expose degraded demo fallback clearly, support practical server-side file uploads, and keep product claims aligned with the implementation.

## Architecture

The existing JSON endpoints remain backward compatible. A new multipart ranking endpoint accepts a job file or text plus a candidate file, adapts the uploaded records through the existing ingestion layer, and passes the same `RankRequest` into `RankerService`.

The latest in-memory ranking is exposed through `/api/rank/latest`. The comparison page loads that run, calls `/api/compare` through the shared frontend API client, and renders the backend response directly: score differences, evidence differences, risks, stronger areas, and verification prompts. Local score subtraction is removed.

The run-ranking page uses multipart upload when a candidate file is selected and JSON otherwise. Any API or parsing failure sets a dedicated degraded state with the exact visible warning: "Live ranking failed. Showing demo fallback."

## Interfaces

- `POST /api/rank` remains JSON-only and unchanged.
- `POST /api/rank/upload` accepts:
  - `job_text`: optional form field
  - `job_file`: optional UTF-8 text file
  - `candidates_file`: required JSON, JSONL, CSV, or `.jsonl.gz`
  - `top_n`: integer form field
- `compareCandidates(a, b)` returns a typed `ComparisonPayload`.
- `rankUploadedCandidates(formData)` returns a `RankingPayload`.

## Error Handling

Malformed files, unsupported formats, duplicate identifiers, and invalid `top_n` values return HTTP 400 with a useful detail message. Frontend failures do not masquerade as live success; demo data remains available but is always labeled as fallback.

## Testing

- FastAPI tests cover multipart JSONL ranking and malformed upload errors.
- Frontend type checking and production build verify the comparison and fallback UI.
- Browser checks verify comparison API usage and the visible fallback warning.
- The full Python suite remains green.

## Documentation

README, final report, and technical audit will describe JD processing as deterministic requirement matrix extraction. Stack claims will list Next.js, TypeScript, Tailwind CSS, FastAPI, and Python without claiming shadcn/ui or Recharts.
