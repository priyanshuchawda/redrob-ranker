"use client";

import { AppShell } from "@/components/AppShell";
import { CandidateTable } from "@/components/CandidateTable";
import { useRankingData } from "@/hooks/useRankingData";

export default function CandidatesPage() {
  const { payload, loading } = useRankingData();
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Candidates</h1>
        <p className="mt-1 text-sm text-slate-600">{loading ? "Loading..." : `${payload?.rankings.length ?? 0} ranked profiles`}</p>
      </div>
      {payload && <CandidateTable rows={payload.rankings} />}
    </AppShell>
  );
}
