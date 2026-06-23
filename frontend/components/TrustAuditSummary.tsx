import type { TrustAuditPayload } from "@/lib/types";

export function TrustAuditSummary({ audit }: { audit: TrustAuditPayload }) {
  const cards = [
    ["Total candidates", audit.total_candidates],
    ["Shortlisted", audit.shortlisted_candidates],
    ["Avg confidence", audit.average_confidence.toFixed(0)],
    ["Avg proof", audit.average_proof_score.toFixed(0)],
    ["High risk", audit.high_risk_candidate_count],
    ["Missing evidence", audit.candidates_with_missing_evidence],
    ["Weak proof / stuffing", audit.keyword_stuffing_or_weak_proof_count],
    ["Location / availability", audit.location_or_availability_risk_count],
    ["Low confidence", audit.low_confidence_count]
  ];
  return (
    <div className="space-y-6">
      {audit.proxy_evaluation_warning && (
        <div className="rounded border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">{audit.proxy_evaluation_warning}</div>
      )}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map(([label, value]) => (
          <div key={label} className="rounded-lg border border-line bg-white p-4 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
          </div>
        ))}
      </div>
      <BarGroup title="Score distribution" values={audit.score_distribution} />
      <BarGroup title="Risk severity counts" values={audit.risk_severity_counts} />
      <BarGroup title="Missing evidence categories" values={audit.missing_evidence_categories} />
      <BarGroup title="Proof versus claim" values={audit.proof_vs_claim_summary} />
    </div>
  );
}

function BarGroup({ title, values }: { title: string; values: Record<string, number> }) {
  const entries = Object.entries(values);
  const max = Math.max(1, ...entries.map(([, value]) => value));
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <div className="mt-4 space-y-3">
        {entries.length ? entries.map(([label, value]) => (
          <div key={label}>
            <div className="flex justify-between text-xs text-slate-600"><span>{label}</span><span>{value}</span></div>
            <div className="mt-1 h-2 rounded bg-slate-100"><div className="h-2 rounded bg-ink" style={{ width: `${(value / max) * 100}%` }} /></div>
          </div>
        )) : <p className="text-sm text-slate-500">No data yet.</p>}
      </div>
    </section>
  );
}
