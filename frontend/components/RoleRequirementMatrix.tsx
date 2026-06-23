import type { RoleRequirementMatrix as RoleRequirementMatrixType } from "@/lib/types";

const listFields = [
  ["Must have", "must_have_skills"],
  ["Strong signals", "strong_signal_skills"],
  ["Good to have", "good_to_have_skills"],
  ["Risk blockers", "risk_blockers"]
] as const;

const textFields = [
  ["Seniority", "seniority_expectations"],
  ["Domain", "domain_expectations"],
  ["Production", "production_expectations"],
  ["Leadership", "leadership_expectations"],
  ["Location", "location_requirements"],
  ["Availability", "availability_requirements"]
] as const;

export function RoleRequirementMatrix({ matrix, compact = false }: { matrix?: RoleRequirementMatrixType; compact?: boolean }) {
  if (!matrix) return null;
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-teal">JD Understanding</p>
          <h2 className="mt-1 text-lg font-semibold text-ink">{matrix.role_title || "Unclear role"}</h2>
          <p className="mt-1 text-sm text-slate-600">Deterministic requirement matrix extracted from the job description.</p>
        </div>
      </div>
      <div className={`mt-4 grid gap-3 ${compact ? "md:grid-cols-2" : "lg:grid-cols-3"}`}>
        {listFields.map(([label, key]) => (
          <MatrixCard key={key} label={label}>
            <BadgeList items={(matrix[key] as string[] | undefined) ?? []} />
          </MatrixCard>
        ))}
        {textFields.map(([label, key]) => (
          <MatrixCard key={key} label={label}>
            <p className="text-sm text-slate-700">{(matrix[key] as string | undefined) || "Unclear from supplied JD."}</p>
          </MatrixCard>
        ))}
      </div>
    </section>
  );
}

function MatrixCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="rounded border border-line bg-slate-50 p-3">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</h3>
      <div className="mt-2">{children}</div>
    </div>
  );
}

function BadgeList({ items }: { items: string[] }) {
  if (!items.length) return <p className="text-sm text-slate-500">Unclear</p>;
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <span key={item} className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-ink ring-1 ring-line">
          {item}
        </span>
      ))}
    </div>
  );
}
