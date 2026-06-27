"use client";

import { AlertTriangle, CheckCircle2, Download, FileSpreadsheet, FileText, LoaderCircle, Play, Upload } from "lucide-react";
import { useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { CandidateTable } from "@/components/CandidateTable";
import { RoleRequirementMatrix } from "@/components/RoleRequirementMatrix";
import { demoRanking, rankJsonCandidates, rankUploadedCandidates } from "@/lib/api";
import { demoPayload } from "@/lib/demoData";
import type { RankingPayload } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const DEFAULT_JOB = "Senior AI Engineer\nMust have: Python, FastAPI, vector search, ranking, evaluation.";

type Status = "ready" | "running" | "completed" | "fallback" | "demo";

export default function RunRankingPage() {
  const [jobText, setJobText] = useState(DEFAULT_JOB);
  const [candidateText, setCandidateText] = useState("");
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [candidateFile, setCandidateFile] = useState<File | null>(null);
  const [topN, setTopN] = useState(100);
  const [payload, setPayload] = useState<RankingPayload | null>(null);
  const [status, setStatus] = useState<Status>("ready");
  const [failureDetail, setFailureDetail] = useState("");

  const inputMode = candidateFile ? "file" : candidateText.trim() ? "pasted" : "empty";
  const canRun = status !== "running" && inputMode !== "empty";
  const pipeline = useMemo(() => pipelineSteps(status, candidateFile, candidateText, payload), [candidateFile, candidateText, payload, status]);

  async function runRanking() {
    setStatus("running");
    setFailureDetail("");
    try {
      if (candidateFile) {
        const formData = new FormData();
        formData.append("candidates_file", candidateFile);
        formData.append("top_n", String(topN));
        if (jobFile) {
          formData.append("job_file", jobFile);
        } else {
          formData.append("job_text", jobText);
        }
        setPayload(await rankUploadedCandidates(formData));
      } else {
        const candidates = candidateText.trim() ? parseCandidateText(candidateText) : undefined;
        setPayload(await rankJsonCandidates({ job_text: jobText, candidates, top_n: topN }));
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
    setJobText(DEFAULT_JOB);
    setCandidateText("");
    setCandidateFile(null);
    setFailureDetail("");
    setStatus("demo");
  }

  return (
    <AppShell>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-cobalt">Deterministic ranking pipeline</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink">Upload candidates and generate output</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Upload candidate files in CSV, JSON, JSONL, NDJSON, or JSONL.GZ. Paste or upload the job description, run the local ranker, then export the challenge-ready CSV/XLSX.
          </p>
        </div>
        <div className="rounded-lg border border-line bg-white px-4 py-3 text-sm shadow-panel">
          <p className="font-semibold text-ink">{statusLabel(status)}</p>
          <p className="mt-1 text-xs text-slate-500">No hosted API calls in the ranking step.</p>
        </div>
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

      <div className="mb-5 grid gap-3 md:grid-cols-3">
        {pipeline.map((step, index) => (
          <PipelineCard key={step.title} index={index + 1} title={step.title} detail={step.detail} done={step.done} active={step.active} />
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-ink">1. Job description</h2>
              <p className="mt-1 text-sm text-slate-600">Paste text or upload `.txt`, `.md`, or `.docx`.</p>
            </div>
            {jobFile && <span className="rounded bg-cobalt/10 px-2.5 py-1 text-xs font-medium text-cobalt">{jobFile.name}</span>}
          </div>
          <textarea
            aria-label="Job description"
            value={jobText}
            onChange={(event) => {
              setJobText(event.target.value);
              if (event.target.value.trim()) setJobFile(null);
            }}
            className="mt-4 min-h-48 w-full rounded border border-line p-3 text-sm leading-6 focus-ring"
          />
          <label className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded border border-line px-3 py-2 text-sm font-medium text-slate-700 focus-ring hover:border-cobalt hover:text-cobalt">
            <FileText size={16} aria-hidden="true" />
            {jobFile ? "Replace JD file" : "Upload JD"}
            <input
              className="sr-only"
              type="file"
              accept=".txt,.md,.docx"
              onChange={async (event) => {
                const file = event.target.files?.[0] ?? null;
                setJobFile(file);
                if (!file) return;
                if (file.name.toLowerCase().endsWith(".docx")) {
                  setJobText(`DOCX selected: ${file.name}. The backend will parse it during ranking.`);
                } else {
                  setJobText(await file.text());
                }
              }}
            />
          </label>
        </section>

        <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-ink">2. Candidate input</h2>
              <p className="mt-1 text-sm text-slate-600">Upload `.csv`, `.json`, `.jsonl`, `.ndjson`, or `.jsonl.gz`; or paste JSON/JSONL.</p>
            </div>
            {candidateFile && <span className="rounded bg-teal/10 px-2.5 py-1 text-xs font-medium text-teal">{candidateFile.name}</span>}
          </div>
          <textarea
            aria-label="Candidate JSON or JSONL"
            value={candidateText}
            onChange={(event) => {
              setCandidateText(event.target.value);
              if (event.target.value.trim()) setCandidateFile(null);
            }}
            placeholder={'Paste a JSON array or JSONL, e.g.\n{"candidate_id":"CAND_0000001","profile":{...},"career_history":[...],"skills":[...],"redrob_signals":{...}}'}
            className="mt-4 min-h-48 w-full rounded border border-line p-3 text-sm leading-6 focus-ring"
          />
          <div className="mt-3 flex flex-wrap items-center gap-3">
            <label className="inline-flex cursor-pointer items-center gap-2 rounded border border-line px-3 py-2 text-sm font-medium text-slate-700 focus-ring hover:border-cobalt hover:text-cobalt">
              <Upload size={16} aria-hidden="true" />
              {candidateFile ? "Replace candidate file" : "Upload candidate file"}
              <input
                className="sr-only"
                type="file"
                accept=".csv,.json,.jsonl,.ndjson,.gz,.jsonl.gz"
                onChange={(event) => {
                  const file = event.target.files?.[0] ?? null;
                  setCandidateFile(file);
                  if (file) setCandidateText("");
                }}
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              Top N
              <input
                type="number"
                min={1}
                max={500}
                value={topN}
                onChange={(event) => setTopN(Math.max(1, Math.min(500, Number(event.target.value) || 1)))}
                className="w-24 rounded border border-line px-3 py-2 text-sm focus-ring"
              />
            </label>
          </div>
        </section>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          disabled={!canRun}
          onClick={runRanking}
          className="focus-ring inline-flex items-center gap-2 rounded bg-ink px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {status === "running" ? <LoaderCircle className="animate-spin" size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
          {status === "running" ? "Ranking candidates" : "Run ranking pipeline"}
        </button>
        <button type="button" onClick={useDemoScenario} className="focus-ring inline-flex items-center gap-2 rounded border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
          Use demo scenario
        </button>
      </div>

      {payload && (
        <div className="mt-6 space-y-6">
          <RunSummary payload={payload} />
          <ExportActions />
          <RoleRequirementMatrix matrix={payload.role_requirements} />
          <CandidateTable rows={payload.rankings} />
        </div>
      )}
    </AppShell>
  );
}

function PipelineCard({ index, title, detail, done, active }: { index: number; title: string; detail: string; done: boolean; active: boolean }) {
  return (
    <div className={`rounded-lg border p-4 shadow-panel ${active ? "border-cobalt bg-cobalt/5" : "border-line bg-white"}`}>
      <div className="flex items-start gap-3">
        <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${done ? "bg-teal text-white" : active ? "bg-cobalt text-white" : "bg-slate-100 text-slate-500"}`}>
          {done ? <CheckCircle2 size={17} aria-hidden="true" /> : index}
        </div>
        <div>
          <h3 className="text-sm font-semibold text-ink">{title}</h3>
          <p className="mt-1 text-xs leading-5 text-slate-600">{detail}</p>
        </div>
      </div>
    </div>
  );
}

function RunSummary({ payload }: { payload: RankingPayload }) {
  const pipeline = payload.metadata.input_pipeline;
  const highRisk = payload.rankings.filter((row) => row.risk_score >= 50).length;
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-ink">3. Ranking output ready</h2>
          <p className="mt-1 text-sm text-slate-600">
            Ranked {payload.rankings.length} candidates from {payload.metadata.candidate_count} loaded records in {payload.metadata.runtime_seconds.toFixed(2)}s.
          </p>
        </div>
        <span className="rounded bg-emerald-50 px-3 py-1 text-xs font-semibold text-teal">Ready to export</span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <SummaryTile label="Candidate file" value={pipeline?.candidate_file ?? "Pasted/demo data"} />
        <SummaryTile label="Job source" value={pipeline?.job_source ?? (payload.metadata.job_supplied ? "Typed job description" : "Default role matrix")} />
        <SummaryTile label="High-risk rows" value={String(highRisk)} />
        <SummaryTile label="Export format" value="CSV + XLSX" />
      </div>
    </section>
  );
}

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-slate-50 px-3 py-2">
      <p className="text-xs font-medium text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold text-ink" title={value}>{value}</p>
    </div>
  );
}

function ExportActions() {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      <ExportButton href={`${API_BASE}/api/exports/submission-xlsx`} icon={FileSpreadsheet} title="Download submission XLSX" detail="Portal-ready spreadsheet" />
      <ExportButton href={`${API_BASE}/api/exports/submission-csv`} icon={Download} title="Download submission CSV" detail="Official challenge columns" />
      <ExportButton href={`${API_BASE}/api/exports/ranked-json`} icon={FileText} title="Download ranked JSON" detail="Full audit payload" />
    </div>
  );
}

function ExportButton({ href, icon: Icon, title, detail }: { href: string; icon: typeof Download; title: string; detail: string }) {
  return (
    <a href={href} className="focus-ring rounded-lg border border-line bg-white p-4 shadow-panel hover:border-cobalt">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded bg-cobalt/10 text-cobalt">
          <Icon size={18} aria-hidden="true" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-ink">{title}</h3>
          <p className="mt-1 text-xs text-slate-600">{detail}</p>
        </div>
      </div>
    </a>
  );
}

function pipelineSteps(status: Status, candidateFile: File | null, candidateText: string, payload: RankingPayload | null) {
  const hasCandidateInput = Boolean(candidateFile || candidateText.trim());
  return [
    { title: "Input", detail: hasCandidateInput ? "Candidate data is selected." : "Upload CSV/JSON/JSONL or paste JSON.", done: hasCandidateInput, active: !hasCandidateInput },
    { title: "Rank", detail: status === "running" ? "Scoring evidence, risk, fit and behavior." : "Run deterministic ranking locally.", done: Boolean(payload), active: status === "running" },
    { title: "Export", detail: payload ? "Submission CSV/XLSX and audit JSON are ready." : "Exports appear after a successful run.", done: Boolean(payload), active: Boolean(payload) }
  ];
}

function statusLabel(status: Status) {
  if (status === "running") return "Running";
  if (status === "completed") return "Completed";
  if (status === "fallback") return "Fallback";
  if (status === "demo") return "Demo";
  return "Ready";
}

function parseCandidateText(text: string) {
  const trimmed = text.trim();
  if (!trimmed) return undefined;
  if (trimmed.startsWith("[")) return JSON.parse(trimmed);
  return trimmed.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}
