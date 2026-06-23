import Link from "next/link";
import type { RankingRow } from "@/lib/types";

export function CandidateTable({ rows }: { rows: RankingRow[] }) {
  return (
    <div className="overflow-hidden rounded-lg border border-line bg-white shadow-panel">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-line text-sm">
          <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-normal text-slate-500">
            <tr>
              {["Rank", "Candidate", "Final", "Fit", "Proof", "Confidence", "Hireability", "Risk", "Main reason"].map((header) => (
                <th key={header} className="px-4 py-3">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {rows.map((row) => (
              <tr key={row.candidate_id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-semibold text-ink">{row.rank}</td>
                <td className="px-4 py-3">
                  <Link className="focus-ring rounded text-cobalt hover:underline" href={`/candidates/${row.candidate_id}`}>
                    {row.candidate_id}
                  </Link>
                </td>
                <td className="px-4 py-3 tabular-nums">{row.final_score.toFixed(0)}</td>
                <td className="px-4 py-3 tabular-nums">{row.fit_score.toFixed(0)}</td>
                <td className="px-4 py-3 tabular-nums">{row.proof_score.toFixed(0)}</td>
                <td className="px-4 py-3 tabular-nums">{row.confidence_score.toFixed(0)}</td>
                <td className="px-4 py-3 tabular-nums">{row.hireability_score.toFixed(0)}</td>
                <td className="px-4 py-3">
                  <span className={`rounded px-2 py-1 text-xs ${row.risk_score >= 50 ? "bg-red-50 text-risk" : "bg-emerald-50 text-teal"}`}>
                    {row.risk_score >= 50 ? "High" : row.risk_score >= 20 ? "Review" : "Low"}
                  </span>
                </td>
                <td className="min-w-80 px-4 py-3 text-slate-600">{row.main_reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
