"use client";

import { AlertTriangle, Clock, Gauge, ShieldCheck, Users } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { CandidateTable } from "@/components/CandidateTable";
import { EvidenceLedgerPreview } from "@/components/EvidenceLedgerPreview";
import { MetricCard } from "@/components/MetricCard";
import { RiskRadar } from "@/components/RiskRadar";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { useRankingData } from "@/hooks/useRankingData";

export default function DashboardPage() {
  const { payload, source, loading, error } = useRankingData();
  const rows = payload?.rankings ?? [];
  const top = rows[0];
  const highRisk = rows.filter((row) => row.risk_score >= 50).length;
  const avgConfidence = rows.length ? rows.reduce((sum, row) => sum + row.confidence_score, 0) / rows.length : 0;

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Dashboard</h1>
          <p className="mt-1 text-sm text-slate-600">Source: {source === "api" ? "FastAPI backend" : "bundled demo output"}</p>
        </div>
      </div>
      {loading && <p className="rounded-lg border border-line bg-white p-4 text-sm text-slate-600">Loading ranking data...</p>}
      {error && <p className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-risk">{error}</p>}
      {payload && (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <MetricCard label="Total candidates" value={payload.metadata.candidate_count} detail="Loaded into ranking run" icon={Users} />
            <MetricCard label="Shortlisted" value={rows.length} detail="Visible ranked candidates" icon={ShieldCheck} />
            <MetricCard label="Avg confidence" value={avgConfidence.toFixed(0)} detail="Normalized confidence score" icon={Gauge} />
            <MetricCard label="High risk" value={highRisk} detail="Profiles requiring review" icon={AlertTriangle} />
            <MetricCard label="Runtime" value={`${payload.metadata.runtime_seconds.toFixed(2)}s`} detail="Backend ranking time" icon={Clock} />
          </div>
          <CandidateTable rows={rows} />
          {top && (
            <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
              <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
                <h2 className="text-base font-semibold text-ink">Score breakdown</h2>
                <div className="mt-4">
                  <ScoreBreakdown row={top as unknown as Record<string, number>} />
                </div>
              </section>
              <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
                <h2 className="text-base font-semibold text-ink">Evidence ledger preview</h2>
                <div className="mt-4">
                  <EvidenceLedgerPreview evidence={top.evidence_ledger.positive_evidence} />
                </div>
              </section>
              <section className="lg:col-span-2">
                <h2 className="mb-3 text-base font-semibold text-ink">Risk radar</h2>
                <RiskRadar risks={top.risks} />
              </section>
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
