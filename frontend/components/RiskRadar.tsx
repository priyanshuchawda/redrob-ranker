import { AlertTriangle } from "lucide-react";
import type { RiskItem } from "@/lib/types";

export function RiskRadar({ risks }: { risks: RiskItem[] }) {
  if (!risks.length) {
    return <p className="rounded-lg border border-line bg-white p-4 text-sm text-slate-600">No structured risk flags from supplied fields.</p>;
  }
  return (
    <div className="grid gap-3">
      {risks.map((risk, index) => (
        <article key={`${risk.risk_type}-${index}`} className="rounded-lg border border-line bg-white p-4 shadow-panel">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-8 w-8 items-center justify-center rounded bg-red-50 text-risk">
              <AlertTriangle size={16} aria-hidden="true" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-sm font-semibold text-ink">{risk.risk_type}</h3>
                <span className="rounded border border-line px-2 py-0.5 text-xs text-slate-600">{risk.severity}</span>
              </div>
              <p className="mt-1 text-sm text-slate-600">{risk.explanation}</p>
              <p className="mt-2 text-xs text-slate-500">Evidence: {risk.evidence}</p>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
