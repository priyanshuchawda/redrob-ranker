"use client";

import { Download, FileJson, Table } from "lucide-react";
import { AppShell } from "@/components/AppShell";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export default function ExportsPage() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink">Exports</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <ExportCard icon={FileJson} title="Ranked JSON" href={`${API_BASE}/api/exports/ranked-json`} />
        <ExportCard icon={Table} title="Ranked CSV" href={`${API_BASE}/api/exports/ranked-csv`} />
      </div>
    </AppShell>
  );
}

function ExportCard({ icon: Icon, title, href }: { icon: typeof Download; title: string; href: string }) {
  return (
    <a href={href} className="focus-ring rounded-lg border border-line bg-white p-5 shadow-panel hover:border-cobalt">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded bg-cobalt/10 text-cobalt">
          <Icon size={18} aria-hidden="true" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-ink">{title}</h2>
          <p className="mt-1 text-sm text-slate-600">Download from FastAPI export endpoint</p>
        </div>
      </div>
    </a>
  );
}
