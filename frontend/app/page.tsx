import Link from "next/link";
import { ArrowRight, BarChart3, FileText, ShieldCheck } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-mist">
      <section className="border-b border-line bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_520px] lg:px-8">
          <div className="flex flex-col justify-center">
            <p className="text-sm font-semibold uppercase tracking-normal text-teal">EvidenceGraph Ranker</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold text-ink sm:text-5xl">Recruiter Intelligence Console</h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-600">
              Rank candidates by role fit, proof strength, confidence, hireability, and risk.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link href="/dashboard" className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-4 py-2.5 text-sm font-semibold text-white">
                Open console <ArrowRight size={16} aria-hidden="true" />
              </Link>
              <Link href="/run-ranking" className="focus-ring inline-flex items-center gap-2 rounded border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
                Run ranking
              </Link>
            </div>
          </div>
          <div className="rounded-lg border border-line bg-slatePanel p-5 text-white shadow-panel">
            <div className="grid grid-cols-3 gap-3">
              {[["Fit", "86"], ["Proof", "82"], ["Risk", "Low"]].map(([label, value]) => (
                <div key={label} className="rounded border border-white/15 bg-white/10 p-3">
                  <p className="text-xs text-white/70">{label}</p>
                  <p className="mt-2 text-2xl font-semibold">{value}</p>
                </div>
              ))}
            </div>
            <div className="mt-5 space-y-3">
              {[
                [ShieldCheck, "Evidence ledger separates claims from proof"],
                [BarChart3, "Score breakdown exposes fit, proof, confidence, hireability, risk"],
                [FileText, "Battle cards and exports are generated from ranked evidence"]
              ].map(([Icon, text]) => {
                const TypedIcon = Icon as typeof ShieldCheck;
                return (
                  <div key={text as string} className="flex items-center gap-3 rounded border border-white/15 bg-white/10 p-3">
                    <TypedIcon size={17} aria-hidden="true" />
                    <span className="text-sm">{text as string}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
