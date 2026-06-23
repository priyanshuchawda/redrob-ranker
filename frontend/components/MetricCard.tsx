import type { LucideIcon } from "lucide-react";

export function MetricCard({
  label,
  value,
  detail,
  icon: Icon
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: LucideIcon;
}) {
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-normal text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
        </div>
        <div className="flex h-9 w-9 items-center justify-center rounded bg-teal/10 text-teal">
          <Icon size={18} aria-hidden="true" />
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-600">{detail}</p>
    </section>
  );
}
