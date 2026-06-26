"use client";

import { AlertTriangle, GitCompare, LoaderCircle, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { useRankingData } from "@/hooks/useRankingData";
import { compareCandidates } from "@/lib/api";
import type { ComparisonPayload, RiskItem } from "@/lib/types";

export default function ComparePage() {
  const { payload, loading: rankingsLoading } = useRankingData();
  const rows = payload?.rankings ?? [];
  const [aId, setAId] = useState("");
  const [bId, setBId] = useState("");
  const [comparison, setComparison] = useState<ComparisonPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (rows.length < 2 || aId || bId) return;
    setAId(rows[0].candidate_id);
    setBId(rows[1].candidate_id);
  }, [aId, bId, rows]);

  async function runComparison() {
    if (!aId || !bId || aId === bId) return;
    setLoading(true);
    setError(null);
    try {
      setComparison(await compareCandidates(aId, bId));
    } catch (err) {
      setComparison(null);
      setError(err instanceof Error ? err.message : "Comparison failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Compare</h1>
      </div>
      <div className="mb-5 flex flex-wrap gap-3">
        <select aria-label="Candidate A" value={aId} onChange={(event) => setAId(event.target.value)} className="rounded border border-line bg-white px-3 py-2 text-sm focus-ring">
          {rows.map((row) => <option key={row.candidate_id}>{row.candidate_id}</option>)}
        </select>
        <select aria-label="Candidate B" value={bId} onChange={(event) => setBId(event.target.value)} className="rounded border border-line bg-white px-3 py-2 text-sm focus-ring">
          {rows.map((row) => <option key={row.candidate_id}>{row.candidate_id}</option>)}
        </select>
        <button
          type="button"
          onClick={runComparison}
          disabled={loading || rankingsLoading || !aId || !bId || aId === bId}
          className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? <LoaderCircle className="animate-spin" size={16} aria-hidden="true" /> : <GitCompare size={16} aria-hidden="true" />}
          Compare candidates
        </button>
      </div>
      {aId === bId && aId && <InlineError message="Choose two different candidates." />}
      {error && <InlineError message={error} />}
      {!comparison && !error && (
        <section className="rounded-lg border border-dashed border-line bg-white px-5 py-10 text-center">
          <GitCompare className="mx-auto text-slate-400" size={28} aria-hidden="true" />
          <p className="mt-3 text-sm text-slate-600">Select two candidates to generate an evidence-backed decision view.</p>
        </section>
      )}
      {comparison && (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <CandidateScore title="Candidate A" candidate={comparison.candidate_a} />
            <CandidateScore title="Candidate B" candidate={comparison.candidate_b} />
          </div>
          <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <div className="flex items-center gap-2">
              <GitCompare size={18} aria-hidden="true" />
              <h2 className="text-base font-semibold text-ink">Decision view</h2>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-700">{comparison.why_a_ranks_above_b}</p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(comparison.score_component_differences).map(([label, value]) => (
                <div key={label} className="rounded border border-line p-3">
                  <p className="text-xs capitalize text-slate-500">{label.replaceAll("_", " ")} delta</p>
                  <p className="mt-1 text-lg font-semibold text-ink">{value > 0 ? "+" : ""}{value.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </section>
          <div className="grid gap-6 lg:grid-cols-2">
            <ListSection title="Where Candidate B is stronger" items={comparison.where_b_is_stronger} />
            <ListSection title="What the recruiter should verify" items={comparison.what_to_verify} />
            {comparison.ai_semantic_comparison?.gemini_enabled && (
              <section className="rounded-lg border border-indigo-100 bg-indigo-50/60 p-5 shadow-panel lg:col-span-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Gemini assisted insight</p>
                <h2 className="mt-1 text-base font-semibold text-ink">AI semantic comparison</h2>
                <p className="mt-3 text-sm text-slate-700">{comparison.ai_semantic_comparison.summary}</p>
                <div className="mt-4 grid gap-4 md:grid-cols-3">
                  <ListInline title="Hidden strengths difference" items={comparison.ai_semantic_comparison.hidden_strengths_difference} />
                  <ListInline title="Risk difference" items={comparison.ai_semantic_comparison.risk_difference} />
                  <ListInline title="Interview checks" items={comparison.ai_semantic_comparison.interview_checks} />
                </div>
                <p className="mt-3 text-xs text-slate-500">Gemini did not generate the final ranking.</p>
              </section>
            )}
            <EvidenceDifferences comparison={comparison} />
            <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
              <div className="flex items-center gap-2">
                <ShieldAlert size={18} aria-hidden="true" />
                <h2 className="text-base font-semibold text-ink">Risk comparison</h2>
              </div>
              <div className="mt-4 grid gap-5 sm:grid-cols-2">
                <RiskList label="Candidate A" risks={comparison.risks_for_a} />
                <RiskList label="Candidate B" risks={comparison.risks_for_b} />
              </div>
            </section>
          </div>
        </div>
      )}
    </AppShell>
  );
}

function ListInline({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h3>
      <p className="mt-2 text-sm text-slate-700">{items.length ? items.join("; ") : "Missing from supplied data"}</p>
    </div>
  );
}

function CandidateScore({ title, candidate }: { title: string; candidate: ComparisonPayload["candidate_a"] }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <h2 className="mt-1 text-base font-semibold text-ink">{candidate.candidate_id}</h2>
      <div className="mt-4">
        <ScoreBreakdown row={candidate as unknown as Record<string, number>} />
      </div>
    </section>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <ul className="mt-3 space-y-2 text-sm text-slate-700">
        {items.map((item) => <li key={item} className="rounded border border-line px-3 py-2">{item}</li>)}
      </ul>
    </section>
  );
}

function EvidenceDifferences({ comparison }: { comparison: ComparisonPayload }) {
  const groups = [
    ["Only Candidate A", comparison.evidence_differences.a_unique_evidence],
    ["Only Candidate B", comparison.evidence_differences.b_unique_evidence],
    ["Shared proof", comparison.evidence_differences.shared_evidence],
    ["Missing for A", comparison.evidence_differences.a_missing],
    ["Missing for B", comparison.evidence_differences.b_missing]
  ] as const;
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Evidence differences</h2>
      <div className="mt-4 space-y-4">
        {groups.map(([label, items]) => (
          <div key={label}>
            <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</h3>
            <p className="mt-1 text-sm text-slate-700">{items.length ? items.join(", ") : "No distinct evidence."}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function RiskList({ label, risks }: { label: string; risks: RiskItem[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-ink">{label}</h3>
      <ul className="mt-2 space-y-2 text-sm text-slate-700">
        {risks.map((risk) => (
          <li key={`${risk.risk_type}-${risk.evidence}`} className="rounded border border-line p-3">
            <span className="font-medium capitalize text-ink">{risk.risk_type.replaceAll("_", " ")}</span>
            <span className="ml-2 text-xs uppercase text-risk">{risk.severity}</span>
            <p className="mt-1">{risk.explanation}</p>
          </li>
        ))}
        {!risks.length && <li>No structured risks detected.</li>}
      </ul>
    </div>
  );
}

function InlineError({ message }: { message: string }) {
  return (
    <div role="alert" className="mb-5 flex items-start gap-3 rounded border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      <AlertTriangle className="mt-0.5 shrink-0" size={18} aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}
