"use client";

import { BarChart3 } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { useRankingData } from "@/hooks/useRankingData";

export default function EvaluationPage() {
  const { payload } = useRankingData();
  const rows = payload?.rankings ?? [];
  const highRisk = rows.filter((row) => row.risk_score >= 50).length;
  const strongProof = rows.filter((row) => row.proof_score >= 50).length;
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Evaluation</h1>
        <p className="mt-1 text-sm text-slate-600">Proxy view unless labels are supplied through the CLI or API.</p>
      </div>
      <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <div className="flex items-center gap-2">
          <BarChart3 size={18} aria-hidden="true" />
          <h2 className="text-base font-semibold text-ink">Proxy checks</h2>
        </div>
        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <div className="rounded border border-line p-4">
            <p className="text-xs text-slate-500">Top K</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{rows.length}</p>
          </div>
          <div className="rounded border border-line p-4">
            <p className="text-xs text-slate-500">Strong proof profiles</p>
            <p className="mt-2 text-2xl font-semibold text-teal">{strongProof}</p>
          </div>
          <div className="rounded border border-line p-4">
            <p className="text-xs text-slate-500">High risk profiles</p>
            <p className="mt-2 text-2xl font-semibold text-risk">{highRisk}</p>
          </div>
        </div>
      </section>
    </AppShell>
  );
}
