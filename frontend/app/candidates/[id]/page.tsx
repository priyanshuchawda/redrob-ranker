"use client";

import { useParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { EvidenceLedgerPanel } from "@/components/EvidenceLedgerPanel";
import { RiskRadar } from "@/components/RiskRadar";
import { RoleRequirementMatrix } from "@/components/RoleRequirementMatrix";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { useRankingData } from "@/hooks/useRankingData";

export default function CandidateDetailPage() {
  const params = useParams<{ id: string }>();
  const { payload, loading } = useRankingData();
  const row = payload?.rankings.find((candidate) => candidate.candidate_id === params.id);

  return (
    <AppShell>
      {loading && <p className="rounded-lg border border-line bg-white p-4 text-sm text-slate-600">Loading candidate...</p>}
      {!loading && !row && <p className="rounded-lg border border-line bg-white p-4 text-sm text-slate-600">Candidate not found.</p>}
      {row && (
        <div className="space-y-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-normal text-teal">Rank {row.rank}</p>
            <h1 className="mt-1 text-2xl font-semibold text-ink">{row.candidate_id}</h1>
            <p className="mt-2 max-w-3xl text-sm text-slate-600">{row.main_reason}</p>
          </div>
          <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
            <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
              <h2 className="text-base font-semibold text-ink">Score breakdown</h2>
              <div className="mt-4">
                <ScoreBreakdown row={row as unknown as Record<string, number>} />
              </div>
            </section>
            <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
              <h2 className="text-base font-semibold text-ink">Recruiter reasoning</h2>
              <div className="mt-4 grid gap-3 text-sm text-slate-700">
                {[
                  ["Why shortlisted", row.reasons.why_shortlisted],
                  ["Best evidence", Array.isArray(row.reasons.best_evidence) ? row.reasons.best_evidence.join("; ") : row.reasons.best_evidence],
                  ["Main concern", row.reasons.main_concern],
                  ["Why not ranked higher", row.reasons.why_not_ranked_higher],
                  ["Interview focus", row.interview_focus.join("; ")],
                  ["Hiring feasibility", row.reasons.hiring_feasibility_summary],
                  ["Risk summary", row.reasons.risk_summary]
                ].map(([label, value]) => (
                  <p key={label as string}><span className="font-semibold text-ink">{label}:</span> {value as string}</p>
                ))}
              </div>
            </section>
          </div>
          <section>
            <RoleRequirementMatrix matrix={payload?.role_requirements} compact />
          </section>
          <EvidenceLedgerPanel row={row} />
          <section>
            <h2 className="mb-3 text-base font-semibold text-ink">Risk flags</h2>
            <RiskRadar risks={row.risks} />
          </section>
          <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <h2 className="text-base font-semibold text-ink">Why not higher</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {row.review_tags.map((tag) => <span key={tag} className="rounded bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-800">{tag}</span>)}
            </div>
          </section>
          <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <h2 className="text-base font-semibold text-ink">Missing evidence</h2>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
              {(row.missing_evidence.length ? row.missing_evidence : ["No major missing evidence."]).map((item) => <li key={item}>{item}</li>)}
            </ul>
          </section>
        </div>
      )}
    </AppShell>
  );
}
