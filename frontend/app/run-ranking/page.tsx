"use client";

import { Play, Upload } from "lucide-react";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { CandidateTable } from "@/components/CandidateTable";
import { demoPayload } from "@/lib/demoData";
import type { RankingPayload } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function RunRankingPage() {
  const [jobText, setJobText] = useState("Senior AI Engineer\nMust have: Python, FastAPI, vector search, ranking, evaluation.");
  const [candidateText, setCandidateText] = useState("");
  const [payload, setPayload] = useState<RankingPayload | null>(null);
  const [status, setStatus] = useState("Ready");

  async function runRanking() {
    setStatus("Running");
    try {
      const candidates = candidateText.trim() ? parseCandidateText(candidateText) : undefined;
      const response = await fetch(`${API_BASE}/api/rank`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_text: jobText, candidates, top_n: 50 })
      });
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      setPayload((await response.json()) as RankingPayload);
      setStatus("Completed");
    } catch {
      setPayload(demoPayload);
      setStatus("Demo fallback loaded");
    }
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Run Ranking</h1>
        <p className="mt-1 text-sm text-slate-600">{status}</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <label className="text-sm font-semibold text-ink" htmlFor="job">Job description</label>
          <textarea id="job" value={jobText} onChange={(event) => setJobText(event.target.value)} className="mt-3 min-h-56 w-full rounded border border-line p-3 text-sm focus-ring" />
        </section>
        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <label className="text-sm font-semibold text-ink" htmlFor="candidates">Candidates JSON or JSONL</label>
          <textarea id="candidates" value={candidateText} onChange={(event) => setCandidateText(event.target.value)} className="mt-3 min-h-56 w-full rounded border border-line p-3 text-sm focus-ring" />
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded border border-line px-3 py-2 text-sm font-medium text-slate-700 focus-ring">
            <Upload size={16} aria-hidden="true" />
            Load file
            <input className="sr-only" type="file" accept=".json,.jsonl,.txt" onChange={async (event) => {
              const file = event.target.files?.[0];
              if (file) setCandidateText(await file.text());
            }} />
          </label>
        </section>
      </div>
      <button onClick={runRanking} className="focus-ring mt-5 inline-flex items-center gap-2 rounded bg-ink px-4 py-2.5 text-sm font-semibold text-white">
        <Play size={16} aria-hidden="true" />
        Run
      </button>
      {payload && (
        <div className="mt-6">
          <CandidateTable rows={payload.rankings} />
        </div>
      )}
    </AppShell>
  );
}

function parseCandidateText(text: string) {
  const trimmed = text.trim();
  if (trimmed.startsWith("[")) return JSON.parse(trimmed);
  return trimmed.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}
