from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .models import RankedCandidate, ScoredCandidate
from .evidence_ledger import build_evidence_ledger
from .fairness import fairness_metadata
from .job_understanding import RoleRequirementMatrix
from .reasoning import generate_structured_reasoning
from .review_tags import generate_review_tags, primary_review_tag
from .risk import build_risk_radar
from .schema import load_candidate_records
from .ai_fusion import enrich_payload_with_fallback_ai

HEADER = ["candidate_id", "rank", "score", "reasoning"]
DEBUG_HEADER = [
    "candidate_id",
    "score",
    "role",
    "seniority",
    "retrieval",
    "ranking",
    "evaluation",
    "profile_evidence",
    "skills",
    "product",
    "production",
    "engineering",
    "leadership",
    "confidence",
    "availability",
    "logistics",
    "risk",
    "current_title",
    "years_of_experience",
    "location",
    "country",
    "relevant_skill_count",
    "evidence_phrases",
    "evidence_concepts",
    "risk_flags",
]
AUDIT_HEADER = ["candidate_id", "rank", "score", "verdict", "reason", "fix_needed"]


def iter_candidates(path: str | Path) -> Iterator[dict]:
    candidate_path = Path(path)
    if candidate_path.suffix.lower() in {".json", ".csv"}:
        for record in load_candidate_records(candidate_path):
            yield record.to_scoring_dict()
        return
    opener = gzip.open if candidate_path.suffix == ".gz" else open
    with opener(candidate_path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    candidate = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON in {candidate_path} at line {line_number}: {exc.msg}"
                    ) from exc
                if not isinstance(candidate, dict):
                    raise ValueError(
                        f"Expected a JSON object in {candidate_path} at line {line_number}"
                    )
                yield candidate


def write_submission(rows: Iterable[RankedCandidate], output_path: str | Path) -> None:
    rows = list(rows)
    submission_scores = _submission_scores(rows)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for row, score in zip(rows, submission_scores):
            writer.writerow([row.candidate_id, row.rank, f"{score:.4f}", row.reasoning])


def _submission_scores(rows: list[RankedCandidate]) -> list[float]:
    if not rows:
        return []
    if max(row.score for row in rows) <= 1.0:
        return [row.score for row in rows]
    top_score = max(row.score for row in rows)
    if top_score <= 0:
        return [0.0 for _row in rows]
    return [max(0.0, min(0.99, (row.score / top_score) * 0.99)) for row in rows]


def write_debug_scores(rows: Iterable[ScoredCandidate], output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(DEBUG_HEADER)
        for row in sorted(rows, key=lambda item: (-item.score, item.candidate_id)):
            features = row.features
            components = row.components
            writer.writerow(
                [
                    row.candidate_id,
                    f"{row.score:.4f}",
                    f"{components.role:.4f}",
                    f"{components.seniority:.4f}",
                    f"{components.retrieval:.4f}",
                    f"{components.ranking:.4f}",
                    f"{components.evaluation:.4f}",
                    f"{components.profile_evidence:.4f}",
                    f"{components.skills:.4f}",
                    f"{components.product:.4f}",
                    f"{components.production:.4f}",
                    f"{components.engineering:.4f}",
                    f"{components.leadership:.4f}",
                    f"{components.confidence:.4f}",
                    f"{components.availability:.4f}",
                    f"{components.logistics:.4f}",
                    f"{components.risk:.4f}",
                    features.current_title,
                    f"{features.years_of_experience:.1f}",
                    features.location,
                    features.country,
                    features.relevant_skill_count,
                    "; ".join(features.evidence_phrases),
                    "; ".join(features.evidence_concepts),
                    "; ".join(features.risk_flags),
                ]
            )


def write_audit(
    ranked_rows: Iterable[RankedCandidate],
    scored_by_id: Mapping[str, ScoredCandidate],
    output_path: str | Path,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(AUDIT_HEADER)
        for row in ranked_rows:
            scored = scored_by_id[row.candidate_id]
            verdict, reason, fix_needed = _audit_verdict(scored)
            writer.writerow([row.candidate_id, row.rank, f"{row.score:.4f}", verdict, reason, fix_needed])


def _audit_verdict(scored: ScoredCandidate) -> tuple[str, str, str]:
    features = scored.features
    components = scored.components
    major_risks = {
        "keyword-stuffed profile",
        "generic AI without shipped retrieval evidence",
        "non-target ML domain",
        "outside India",
        "stale profile",
        "low recruiter response",
    }
    risk_hits = [flag for flag in features.risk_flags if flag in major_risks]
    evidence_total = components.retrieval + components.ranking + components.evaluation
    strong_evidence = evidence_total >= 24
    moderate_evidence = evidence_total >= 18
    good_logistics = "outside India" not in features.risk_flags and components.logistics >= 6
    good_availability = components.availability >= 11.0

    if strong_evidence and good_logistics and good_availability and not risk_hits:
        return "A", "Recruiter-trustable production search/ranking fit.", ""
    if risk_hits:
        return "C", "Weak top-100 confidence due to evidence or risk flags.", "; ".join(risk_hits)
    if not moderate_evidence:
        return "B", "Plausible fit; manually review evidence depth.", "review evidence depth"
    return "B", "Plausible fit with one or more calibration concerns.", "; ".join(features.risk_flags)


def build_product_ranking_output(
    scored_rows: Iterable[ScoredCandidate],
    ranked_rows: Iterable[RankedCandidate],
    *,
    role_requirements: RoleRequirementMatrix,
    top_n: int,
    runtime_seconds: float,
    job_supplied: bool,
    data_quality_report: dict | None = None,
) -> dict:
    scored_by_id = {row.candidate_id: row for row in scored_rows}
    rankings: list[dict] = []
    ranked_list = list(ranked_rows)
    for ranked in ranked_list:
        scored = scored_by_id[ranked.candidate_id]
        ledger = build_evidence_ledger(scored, ranked.rank)
        structured = generate_structured_reasoning(scored, ledger)
        risks = build_risk_radar(scored, role_requirements)
        review_tags = generate_review_tags(scored, ledger)
        rankings.append(
            {
                "rank": ranked.rank,
                "candidate_id": ranked.candidate_id,
                "final_score": scored.product_scores.final_score,
                "fit_score": scored.product_scores.fit_score,
                "proof_score": scored.product_scores.proof_score,
                "confidence_score": scored.product_scores.confidence_score,
                "hireability_score": scored.product_scores.hireability_score,
                "risk_score": scored.product_scores.risk_score,
                "main_reason": structured["why_shortlisted"],
                "reasons": structured,
                "risks": risks,
                "review_tag": primary_review_tag(scored, ledger),
                "review_tags": review_tags,
                "missing_evidence": ledger["missing_evidence"],
                "interview_focus": ledger["interview_focus"],
                "evidence_ledger": ledger,
                "components": _components_dict(scored),
            }
        )
    payload = {
        "metadata": {
            "project": "EvidenceGraph Ranker",
            "created_at": _created_at(),
            "candidate_count": len(scored_by_id),
            "top_n": top_n,
            "runtime_seconds": round(runtime_seconds, 4),
            "job_supplied": job_supplied,
            **fairness_metadata(),
        },
        "role_requirements": role_requirements.to_dict(),
        "rankings": rankings,
        "data_quality": data_quality_report or {},
    }
    return enrich_payload_with_fallback_ai(payload)


def write_product_outputs(payload: dict, output_dir: str | Path, csv_filename: str = "ranked_candidates.csv") -> None:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "ranked_candidates.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (directory / "evidence_ledgers.json").write_text(
        json.dumps([row["evidence_ledger"] for row in payload["rankings"]], indent=2),
        encoding="utf-8",
    )
    (directory / "runtime_summary.json").write_text(
        json.dumps(payload["metadata"], indent=2),
        encoding="utf-8",
    )
    _write_product_csv(payload["rankings"], directory / csv_filename)


def write_product_json(payload: dict, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_product_csv(rankings: Iterable[dict], output_path: str | Path) -> None:
    _write_product_csv(rankings, Path(output_path))


def _write_product_csv(rankings: Iterable[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank",
        "candidate_id",
        "final_score",
        "fit_score",
        "proof_score",
        "confidence_score",
        "hireability_score",
        "risk_score",
        "review_tag",
        "main_reason",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rankings:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _components_dict(scored: ScoredCandidate) -> dict:
    return {
        "role": scored.components.role,
        "seniority": scored.components.seniority,
        "retrieval": scored.components.retrieval,
        "ranking": scored.components.ranking,
        "evaluation": scored.components.evaluation,
        "profile_evidence": scored.components.profile_evidence,
        "skills": scored.components.skills,
        "product": scored.components.product,
        "production": scored.components.production,
        "engineering": scored.components.engineering,
        "leadership": scored.components.leadership,
        "confidence": scored.components.confidence,
        "availability": scored.components.availability,
        "logistics": scored.components.logistics,
        "risk": scored.components.risk,
        "total": scored.components.total,
    }


def _created_at() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
