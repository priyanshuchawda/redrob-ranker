"use client";

import { Download, FileJson, FileSpreadsheet, Table } from "lucide-react";
import { AppShell } from "@/components/AppShell";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function ExportsPage() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Exports</h1>
        <p className="mt-1 text-sm text-slate-600">Download the latest ranking run from FastAPI. Run a file upload first to refresh these outputs.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <ExportCard icon={FileSpreadsheet} title="Submission XLSX" detail="Portal-ready candidate_id/rank/score/reasoning spreadsheet" href={`${API_BASE}/api/exports/submission-xlsx`} />
        <ExportCard icon={Table} title="Submission CSV" detail="Official challenge CSV columns" href={`${API_BASE}/api/exports/submission-csv`} />
        <ExportCard icon={FileJson} title="Ranked JSON" detail="Full evidence, risk, reasoning and audit payload" href={`${API_BASE}/api/exports/ranked-json`} />
        <ExportCard icon={Table} title="Product CSV" detail="Recruiter console score breakdown CSV" href={`${API_BASE}/api/exports/ranked-csv`} />
      </div>
    </AppShell>
  );
}

function ExportCard({ icon: Icon, title, detail, href }: { icon: typeof Download; title: string; detail: string; href: string }) {
  return (
    <a href={href} className="focus-ring rounded-lg border border-line bg-white p-5 shadow-panel hover:border-cobalt">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded bg-cobalt/10 text-cobalt">
          <Icon size={18} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-ink">{title}</h2>
          <p className="mt-1 text-sm text-slate-600">{detail}</p>
        </div>
      </div>
    </a>
  );
}
