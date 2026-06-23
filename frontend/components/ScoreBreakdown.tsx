const scoreFields = [
  ["fit_score", "Fit"],
  ["proof_score", "Proof"],
  ["confidence_score", "Confidence"],
  ["hireability_score", "Hireability"],
  ["risk_score", "Risk"]
] as const;

export function ScoreBreakdown({ row }: { row: Record<string, number> }) {
  return (
    <div className="space-y-3">
      {scoreFields.map(([key, label]) => {
        const value = Math.max(0, Math.min(100, Number(row[key] ?? 0)));
        const color = key === "risk_score" ? "bg-risk" : key === "proof_score" ? "bg-cobalt" : "bg-teal";
        return (
          <div key={key}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">{label}</span>
              <span className="tabular-nums text-slate-600">{value.toFixed(0)}</span>
            </div>
            <div className="h-2 rounded bg-slate-100">
              <div className={`h-2 rounded ${color}`} style={{ width: `${value}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
