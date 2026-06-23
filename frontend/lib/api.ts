import { demoPayload } from "./demoData";
import type { RankingPayload } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchRanking(): Promise<{ payload: RankingPayload; source: "api" | "demo" }> {
  try {
    const response = await fetch(`${API_BASE}/api/rank`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ top_n: 50 }),
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

export async function compareCandidates(candidateAId: string, candidateBId: string) {
  const response = await fetch(`${API_BASE}/api/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_a_id: candidateAId, candidate_b_id: candidateBId }),
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Comparison API failed");
  }
  return response.json();
}
