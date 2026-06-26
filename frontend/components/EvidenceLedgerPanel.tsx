"use client";

import { useMemo, useState } from "react";
import type { EvidenceItem, RankingRow, RiskItem } from "@/lib/types";

type Tab = "positive" | "negative" | "missing" | "risks";

export function EvidenceLedgerPanel({ row }: { row: RankingRow }) {
  const [tab, setTab] = useState<Tab>("positive");
  const tabs = useMemo(
    () => [
      ["positive", `Positive evidence (${row.evidence_ledger.positive_evidence.length})`],
      ["negative", `Negative evidence (${row.evidence_ledger.negative_evidence.length})`],
      ["missing", `Missing evidence (${row.evidence_ledger.missing_evidence.length})`],
      ["risks", `Risks (${row.risks.length})`]
    ] as const,
    [row]
  );
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Clickable Evidence Ledger</h2>
      <p className="mt-1 text-sm text-slate-600">Every visible claim is grounded in candidate fields or marked missing.</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {tabs.map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} className={`rounded px-3 py-1.5 text-sm font-medium ${tab === key ? "bg-ink text-white" : "bg-slate-100 text-slate-700"}`}>
            {label}
          </button>
        ))}
      </div>
      <div className="mt-4 space-y-3">
        {tab === "positive" && <EvidenceList items={row.evidence_ledger.positive_evidence} tone="positive" />}
        {tab === "negative" && <EvidenceList items={row.evidence_ledger.negative_evidence} tone="negative" />}
        {tab === "missing" && <MissingList items={row.evidence_ledger.missing_evidence} />}
        {tab === "risks" && <RiskList items={row.risks} />}
      </div>
    </section>
  );
}

function EvidenceList({ items, tone }: { items: EvidenceItem[]; tone: "positive" | "negative" }) {
  if (!items.length) return <p className="rounded border border-line bg-slate-50 p-3 text-sm text-slate-500">No {tone} evidence items.</p>;
  return (
    <>
      {items.map((item, index) => (
        <article key={`${item.source_field}-${item.concept}-${index}`} className={`rounded border p-4 ${tone === "positive" ? "border-emerald-200 bg-emerald-50/50" : "border-red-200 bg-red-50/50"}`}>
          <div className="flex flex-wrap gap-2">
            <Badge value={item.claim_or_proof} />
            <Badge value={item.evidence_type} />
            <Badge value={item.polarity} />
          </div>
          <h3 className="mt-3 text-sm font-semibold text-ink">{item.concept}</h3>
          <p className="mt-1 text-xs text-slate-500">Source: {item.source_field}</p>
          <p className="mt-2 text-sm text-slate-700">{item.snippet}</p>
          <div className="mt-3 grid gap-2 text-xs text-slate-600 sm:grid-cols-3">
            <span>Strength: {item.strength}</span>
            <span>Confidence: {(item.confidence * 100).toFixed(0)}%</span>
            <span>Score impact: {item.score_impact > 0 ? "+" : ""}{item.score_impact}</span>
          </div>
        </article>
      ))}
    </>
  );
}

function MissingList({ items }: { items: string[] }) {
  if (!items.length) return <p className="rounded border border-line bg-slate-50 p-3 text-sm text-slate-500">No missing evidence surfaced.</p>;
  return <ul className="space-y-2">{items.map((item) => <li key={item} className="rounded border border-line bg-slate-50 px-3 py-2 text-sm text-slate-700">{item}</li>)}</ul>;
}

function RiskList({ items }: { items: RiskItem[] }) {
  if (!items.length) return <p className="rounded border border-line bg-slate-50 p-3 text-sm text-slate-500">No structured risks surfaced.</p>;
  return <ul className="space-y-2">{items.map((risk) => <li key={`${risk.risk_type}-${risk.evidence}`} className="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-900"><strong>{risk.risk_type}</strong> ({risk.severity}): {risk.explanation}</li>)}</ul>;
}

function Badge({ value }: { value: string }) {
  const normalized = value.replaceAll("_", " ");
  const tone = value === "strong_proof" ? "bg-emerald-600 text-white" : value === "proof" ? "bg-emerald-100 text-emerald-800" : value === "claim" ? "bg-amber-100 text-amber-800" : "bg-white text-slate-700";
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ring-black/5 ${tone}`}>{normalized}</span>;
}
