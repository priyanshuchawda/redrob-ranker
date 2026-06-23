"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Download, GitCompare, LayoutDashboard, Play, Shield, ShieldCheck, Users } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/run-ranking", label: "Run Ranking", icon: Play },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/trust-audit", label: "Trust Audit", icon: ShieldCheck },
  { href: "/evaluation", label: "Evaluation", icon: BarChart3 },
  { href: "/exports", label: "Exports", icon: Download }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-mist">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded bg-ink text-white">
            <Shield size={18} aria-hidden="true" />
          </div>
          <div>
            <div className="text-sm font-semibold text-ink">Recruiter Intelligence</div>
            <div className="text-xs text-slate-500">EvidenceGraph Ranker</div>
          </div>
        </div>
        <nav className="p-3" aria-label="Main navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`focus-ring mb-1 flex items-center gap-3 rounded px-3 py-2 text-sm ${
                  active ? "bg-ink text-white" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon size={17} aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
