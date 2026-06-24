import type { AIContextualFit, AIJDInsight, AIRecruiterExplanation, SignalFusionSummary } from "@/lib/types";

export function AIJDInsightCard({ insight }: { insight?: AIJDInsight }) {
  if (!insight?.gemini_enabled) return null;
  return (
    <section className="rounded-lg border border-indigo-100 bg-indigo-50/60 p-5 shadow-panel">
      <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Gemini assisted insight</p>
      <h2 className="mt-1 text-base font-semibold text-ink">AI JD Insight</h2>
      <p className="mt-2 text-sm text-slate-700">Role archetype: {insight.role_archetype}</p>
      <TagList title="Semantic synonyms" items={insight.semantic_skill_synonyms} />
      <TagList title="Interview focus" items={insight.interview_focus_areas} />
      <p className="mt-3 text-xs text-slate-500">Model: {insight.model_used}. Deterministic ranking remains primary.</p>
    </section>
  );
}

export function AIContextualFitCard({ fit, hiddenGem, reason }: { fit?: AIContextualFit; hiddenGem?: boolean; reason?: string }) {
  if (!fit?.gemini_enabled) return null;
  return (
    <section className="rounded-lg border border-indigo-100 bg-indigo-50/60 p-5 shadow-panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Gemini assisted insight</p>
          <h2 className="mt-1 text-base font-semibold text-ink">AI Contextual Fit</h2>
        </div>
        {hiddenGem && <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-teal">Hidden Gem</span>}
      </div>
      <p className="mt-3 text-3xl font-semibold text-ink">{fit.contextual_fit_score}</p>
      <p className="mt-2 text-sm text-slate-700">{fit.semantic_fit_reason}</p>
      {hiddenGem && reason && <p className="mt-2 text-sm font-medium text-teal">{reason}</p>}
      <TagList title="Hidden strengths" items={fit.hidden_strengths} />
      <TagList title="Interview checks" items={fit.recommended_interview_checks} />
      <p className="mt-3 text-xs text-slate-500">This score does not overwrite the deterministic final ranking.</p>
    </section>
  );
}

export function AIRecruiterExplanationCard({ explanation }: { explanation?: AIRecruiterExplanation }) {
  if (!explanation?.gemini_enabled) return null;
  return (
    <section className="rounded-lg border border-indigo-100 bg-white p-5 shadow-panel">
      <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Gemini assisted insight</p>
      <h2 className="mt-1 text-base font-semibold text-ink">AI Recruiter Explanation</h2>
      <p className="mt-3 text-sm text-slate-700">{explanation.executive_summary}</p>
      <TagList title="Why shortlisted" items={explanation.why_shortlisted} />
      <TagList title="Concerns" items={explanation.concerns} />
      <TagList title="Interview questions" items={explanation.interview_questions} />
      <p className="mt-3 text-xs text-slate-500">{explanation.final_recruiter_note}</p>
    </section>
  );
}

export function SignalFusionCard({ summary }: { summary?: SignalFusionSummary }) {
  if (!summary) return null;
  const items = [
    ["Role fit", summary.role_fit],
    ["Proof", summary.proof_strength],
    ["Context", summary.contextual_relevance],
    ["Behavior", summary.activity_or_behavioral_signal],
    ["Hireability", summary.hireability],
    ["Risk", summary.risk]
  ];
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
      <h2 className="text-base font-semibold text-ink">Signal Fusion overview</h2>
      <p className="mt-2 text-sm text-slate-600">{summary.summary}</p>
      <div className="mt-4 grid gap-2 sm:grid-cols-3 lg:grid-cols-6">
        {items.map(([label, value]) => (
          <div key={label} className="rounded border border-line px-3 py-2">
            <p className="text-xs text-slate-500">{label}</p>
            <p className="text-sm font-semibold capitalize text-ink">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function TagList({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="mt-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {items.map((item) => <span key={item} className="rounded bg-white px-2.5 py-1 text-xs text-slate-700 shadow-sm">{item}</span>)}
      </div>
    </div>
  );
}
