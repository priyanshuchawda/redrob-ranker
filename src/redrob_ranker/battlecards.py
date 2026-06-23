from __future__ import annotations

import json
from pathlib import Path


def render_battlecards(ranking_payload: dict, top_n: int = 10) -> str:
    rows = ranking_payload.get("rankings", [])[:top_n]
    lines = ["# Candidate Battle Cards", ""]
    for row in rows:
        reasons = row.get("reasons", {})
        lines.extend(
            [
                f"## Rank {row.get('rank')} - Candidate {row.get('candidate_id')}",
                "",
                f"- Final score: {row.get('final_score')}",
                f"- Why shortlisted: {reasons.get('why_shortlisted', row.get('main_reason', 'Unclear.'))}",
                f"- Best evidence: {_join(reasons.get('best_evidence', []))}",
                f"- Main concern: {reasons.get('main_concern', 'Unclear.')}",
                f"- Why not ranked higher: {reasons.get('why_not_ranked_higher', 'Unclear.')}",
                f"- Interview focus: {_join(reasons.get('interview_focus', row.get('interview_focus', [])))}",
                f"- Hiring feasibility: {reasons.get('hiring_feasibility_summary', 'Unclear.')}",
                f"- Risk summary: {reasons.get('risk_summary', 'No structured risk flags.')}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def write_battlecards(ranking_path: str | Path, output_path: str | Path, top_n: int = 10) -> None:
    payload = json.loads(Path(ranking_path).read_text(encoding="utf-8"))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_battlecards(payload, top_n=top_n), encoding="utf-8")


def _join(items: object) -> str:
    if isinstance(items, list):
        return "; ".join(str(item) for item in items) if items else "Unclear."
    return str(items) if items else "Unclear."

