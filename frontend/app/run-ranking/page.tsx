"use client";

import { AlertTriangle, FileText, LoaderCircle, Play, Upload } from "lucide-react";
import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { CandidateTable } from "@/components/CandidateTable";
import { RoleRequirementMatrix } from "@/components/RoleRequirementMatrix";
import { demoRanking, rankUploadedCandidates } from "@/lib/api";
import { demoPayload } from "@/lib/demoData";
import type { RankingPayload } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function RunRankingPage() {
  const [jobText, setJobText] = useState("Senior AI Engineer\nMust have: Python, FastAPI, vector search, ranking, evaluation.");
  const [candidateText, setCandidateText] = useState("");
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [candidateFile, setCandidateFile] = useState<File | null>(null);
  const [payload, setPayload] = useState<RankingPayload | null>(null);
  const [status, setStatus] = useState<"ready" | "running" | "completed" | "fallback" | "demo">("ready");
  const [failureDetail, setFailureDetail] = useState("");

  async function runRanking() {
    setStatus("running");
    setFailureDetail("");
    try {
      if (candidateFile) {
        const formData = new FormData();
        formData.append("candidates_file", candidateFile);
        formData.append("top_n", "50");
        if (jobFile) {
          formData.append("job_file", jobFile);
        } else {
          formData.append("job_text", jobText);
        }
        setPayload(await rankUploadedCandidates(formData));
      } else {
        const candidates = candidateText.trim() ? parseCandidateText(candidateText) : undefined;
        const response = await fetch(`${API_BASE}/api/rank`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_text: jobText, candidates, top_n: 50 })
        });
        if (!response.ok) throw new Error(`API returned ${response.status}`);
        setPayload((await response.json()) as RankingPayload);
      }
      setStatus("completed");
    } catch (error) {
      setPayload(demoPayload);
      setFailureDetail(error instanceof Error ? error.message : "Unknown live ranking error");
      setStatus("fallback");
    }
  }

  function useDemoScenario() {
    const demo = demoRanking();
    setPayload(demo.payload);
    setJobText("Senior AI Engineer\nMust have: Python, FastAPI, vector search, ranking, evaluation.");
    setCandidateText("Demo scenario loaded intentionally: CAND_DEMO_001 versus CAND_DEMO_002.");
    setFailureDetail("");
    setStatus("demo");
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Run Ranking</h1>
        <p className="mt-1 text-sm text-slate-600">
          {status === "ready" && "Ready"}
          {status === "running" && "Running deterministic ranking"}
          {status === "completed" && "Live ranking completed"}
          {status === "demo" && "Demo scenario loaded"}
          {status === "fallback" && "Demo fallback active"}
        </p>
      </div>
      {status === "fallback" && (
        <div role="alert" className="mb-5 flex items-start gap-3 rounded border border-red-200 bg-red-50 p-4 text-red-900">
          <AlertTriangle className="mt-0.5 shrink-0" size={19} aria-hidden="true" />
          <div>
            <p className="text-sm font-semibold">Live ranking failed. Showing demo fallback.</p>
            <p className="mt-1 text-xs text-red-700">{failureDetail}</p>
          </div>
        </div>
      )}
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <label className="text-sm font-semibold text-ink" htmlFor="job">Job description</label>
          <textarea id="job" value={jobText} onChange={(event) => setJobText(event.target.value)} className="mt-3 min-h-56 w-full rounded border border-line p-3 text-sm focus-ring" />
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded border border-line px-3 py-2 text-sm font-medium text-slate-700 focus-ring">
            <FileText size={16} aria-hidden="true" />
            {jobFile ? jobFile.name : "Upload JD"}
            <input className="sr-only" type="file" accept=".txt,.md" onChange={async (event) => {
              const file = event.target.files?.[0] ?? null;
              setJobFile(file);
              if (file) setJobText(await file.text());
            }} />
          </label>
        </section>
        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <label className="text-sm font-semibold text-ink" htmlFor="candidates">Candidates JSON or JSONL</label>
          <textarea id="candidates" value={candidateText} onChange={(event) => {
            setCandidateText(event.target.value);
            if (event.target.value.trim()) setCandidateFile(null);
          }} className="mt-3 min-h-56 w-full rounded border border-line p-3 text-sm focus-ring" />
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded border border-line px-3 py-2 text-sm font-medium text-slate-700 focus-ring">
            <Upload size={16} aria-hidden="true" />
            {candidateFile ? candidateFile.name : "Upload candidate file"}
            <input className="sr-only" type="file" accept=".json,.jsonl,.ndjson,.jsonl.gz,.csv" onChange={(event) => {
              const file = event.target.files?.[0] ?? null;
              setCandidateFile(file);
              if (file) setCandidateText("");
            }} />
          </label>
        </section>
      </div>
      <div className="mt-5 flex flex-wrap gap-3">
        <button disabled={status === "running"} onClick={runRanking} className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60">
          {status === "running" ? <LoaderCircle className="animate-spin" size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
          {status === "running" ? "Ranking" : "Run"}
        </button>
        <button type="button" onClick={useDemoScenario} className="focus-ring inline-flex items-center gap-2 rounded border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
          Use Demo Scenario
        </button>
      </div>
      {payload && (
        <div className="mt-6 space-y-6">
          <RoleRequirementMatrix matrix={payload.role_requirements} />
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
