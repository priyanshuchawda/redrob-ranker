import { demoPayload } from "./demoData";
import type { ComparisonPayload, RankingPayload, TrustAuditPayload } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchRanking(): Promise<{ payload: RankingPayload; source: "api" | "demo" }> {
  try {
    const response = await fetch(`${API_BASE}/api/rank/latest`, {
      cache: "no-store"
    });
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    return { payload: (await response.json()) as RankingPayload, source: "api" };
  } catch {
    return { payload: demoPayload, source: "demo" };
  }
}

export function demoRanking(): { payload: RankingPayload; source: "demo" } {
  return { payload: demoPayload, source: "demo" };
}

export async function rankUploadedCandidates(formData: FormData): Promise<RankingPayload> {
  const response = await fetch(`${API_BASE}/api/rank/upload`, {
    method: "POST",
    body: formData,
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await apiErrorMessage(response, "Uploaded ranking failed"));
  }
  return response.json() as Promise<RankingPayload>;
}

export async function compareCandidates(candidateAId: string, candidateBId: string): Promise<ComparisonPayload> {
  const response = await fetch(`${API_BASE}/api/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_a_id: candidateAId, candidate_b_id: candidateBId }),
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(await apiErrorMessage(response, "Comparison API failed"));
  }
  return response.json() as Promise<ComparisonPayload>;
}

export async function fetchTrustAudit(): Promise<TrustAuditPayload> {
  const response = await fetch(`${API_BASE}/api/trust-audit`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(await apiErrorMessage(response, "Trust audit API failed"));
  }
  return response.json() as Promise<TrustAuditPayload>;
}

async function apiErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail || `${fallback} (${response.status})`;
  } catch {
    return `${fallback} (${response.status})`;
  }
}
