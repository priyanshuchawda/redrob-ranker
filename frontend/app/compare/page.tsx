"use client";

import { GitCompare } from "lucide-react";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { useRankingData } from "@/hooks/useRankingData";

export default function ComparePage() {
  const { payload } = useRankingData();
  const rows = payload?.rankings ?? [];
  const [aId, setAId] = useState("CAND_DEMO_001");
  const [bId, setBId] = useState("CAND_DEMO_002");
  const a = rows.find((row) => row.candidate_id === aId) ?? rows[0];
  const b = rows.find((row) => row.candidate_id === bId) ?? rows[1];
  const diffs = useMemo(() => {
    if (!a || !b) return [];
    return [
      ["Final", a.final_score - b.final_score],
      ["Fit", a.fit_score - b.fit_score],
      ["Proof", a.proof_score - b.proof_score],
      ["Confidence", a.confidence_score - b.confidence_score],
      ["Hireability", a.hireability_score - b.hireability_score],
      ["Risk", a.risk_score - b.risk_score]
    ];
  }, [a, b]);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Compare</h1>
      </div>
      <div className="mb-5 flex flex-wrap gap-3">
        <select value={aId} onChange={(event) => setAId(event.target.value)} className="rounded border border-line bg-white px-3 py-2 text-sm focus-ring">
          {rows.map((row) => <option key={row.candidate_id}>{row.candidate_id}</option>)}
        </select>
        <select value={bId} onChange={(event) => setBId(event.target.value)} className="rounded border border-line bg-white px-3 py-2 text-sm focus-ring">
          {rows.map((row) => <option key={row.candidate_id}>{row.candidate_id}</option>)}
        </select>
      </div>
      {a && b && (
        <div className="grid gap-6 lg:grid-cols-2">
          {[a, b].map((row) => (
            <section key={row.candidate_id} className="rounded-lg border border-line bg-white p-5 shadow-panel">
              <h2 className="text-base font-semibold text-ink">{row.candidate_id}</h2>
              <p className="mt-2 text-sm text-slate-600">{row.main_reason}</p>
              <div className="mt-4">
                <ScoreBreakdown row={row as unknown as Record<string, number>} />
              </div>
            </section>
          ))}
          <section className="rounded-lg border border-line bg-white p-5 shadow-panel lg:col-span-2">
            <div className="flex items-center gap-2">
              <GitCompare size={18} aria-hidden="true" />
              <h2 className="text-base font-semibold text-ink">Decision view</h2>
            </div>
            <p className="mt-3 text-sm text-slate-700">
              {a.candidate_id} ranks above {b.candidate_id} when its final score is higher; verify any negative risk delta before outreach.
            </p>
            <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {diffs.map(([label, value]) => (
                <div key={label as string} className="rounded border border-line p-3">
                  <p className="text-xs text-slate-500">{label as string} delta</p>
                  <p className={`mt-1 text-lg font-semibold ${(value as number) >= 0 ? "text-teal" : "text-risk"}`}>{(value as number).toFixed(1)}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <div>
                <h3 className="text-sm font-semibold text-ink">Where B is stronger</h3>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
                  {diffs.filter(([, value]) => (value as number) < 0).map(([label]) => <li key={label as string}>{label as string}</li>)}
                  {!diffs.some(([, value]) => (value as number) < 0) && <li>No scored component advantage.</li>}
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-ink">Interview recommendation</h3>
                <p className="mt-2 text-sm text-slate-700">{a.interview_focus[0] ?? "Verify production ownership."}</p>
              </div>
            </div>
          </section>
        </div>
      )}
    </AppShell>
  );
}
