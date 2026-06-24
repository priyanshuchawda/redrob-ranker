"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { TrustAuditSummary } from "@/components/TrustAuditSummary";
import { fetchTrustAudit } from "@/lib/api";
import type { TrustAuditPayload } from "@/lib/types";

export default function TrustAuditPage() {
  const [audit, setAudit] = useState<TrustAuditPayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchTrustAudit().then(setAudit).catch((err: Error) => setError(err.message));
  }, []);

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Trust Audit</h1>
        <p className="mt-1 text-sm text-slate-600">Limitations, risk and proof-health summary from the latest ranking payload.</p>
      </div>
      {error && <div role="alert" className="rounded border border-red-200 bg-red-50 p-4 text-sm text-risk">{error}</div>}
      {!audit && !error && <p className="rounded-lg border border-line bg-white p-4 text-sm text-slate-600">Loading trust audit...</p>}
      {audit && (
        <div className="space-y-6">
          {audit.ai_summary?.gemini_enabled && (
            <section className="rounded-lg border border-indigo-100 bg-indigo-50/60 p-5 shadow-panel">
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Gemini assisted insight</p>
              <h2 className="mt-1 text-base font-semibold text-ink">AI verification priorities</h2>
              <p className="mt-2 text-sm text-slate-700">{audit.ai_summary.summary}</p>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
                {audit.ai_summary.verification_priorities.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </section>
          )}
          <TrustAuditSummary audit={audit} />
        </div>
      )}
    </AppShell>
  );
}
