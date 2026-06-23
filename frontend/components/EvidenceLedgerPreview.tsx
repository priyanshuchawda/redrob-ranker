import type { EvidenceItem } from "@/lib/types";

export function EvidenceLedgerPreview({ evidence }: { evidence: EvidenceItem[] }) {
  const items = evidence.slice(0, 5);
  if (!items.length) {
    return <p className="text-sm text-slate-600">No positive evidence extracted from supplied fields.</p>;
  }
  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <article key={`${item.concept}-${index}`} className="rounded-lg border border-line bg-white p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold text-ink">{item.concept}</span>
            <span className="rounded border border-line px-2 py-0.5 text-xs text-slate-600">{item.claim_or_proof}</span>
            <span className="rounded border border-line px-2 py-0.5 text-xs text-slate-600">{item.strength}</span>
          </div>
          <p className="mt-2 text-sm text-slate-700">{item.snippet}</p>
          <p className="mt-2 text-xs text-slate-500">{item.source_field}</p>
        </article>
      ))}
    </div>
  );
}
