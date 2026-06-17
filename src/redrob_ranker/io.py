from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .models import RankedCandidate, ScoredCandidate

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
    "availability",
    "logistics",
    "risk",
    "current_title",
    "years_of_experience",
    "location",
    "country",
    "relevant_skill_count",
    "evidence_phrases",
    "risk_flags",
]
AUDIT_HEADER = ["candidate_id", "rank", "score", "verdict", "reason", "fix_needed"]


def iter_candidates(path: str | Path) -> Iterator[dict]:
    candidate_path = Path(path)
    opener = gzip.open if candidate_path.suffix == ".gz" else open
    with opener(candidate_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def write_submission(rows: Iterable[RankedCandidate], output_path: str | Path) -> None:
    path = Path(output_path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for row in rows:
            writer.writerow([row.candidate_id, row.rank, f"{row.score:.4f}", row.reasoning])


def write_debug_scores(rows: Iterable[ScoredCandidate], output_path: str | Path) -> None:
    path = Path(output_path)
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
                    f"{components.availability:.4f}",
                    f"{components.logistics:.4f}",
                    f"{components.risk:.4f}",
                    features.current_title,
                    f"{features.years_of_experience:.1f}",
                    features.location,
                    features.country,
                    features.relevant_skill_count,
                    "; ".join(features.evidence_phrases),
                    "; ".join(features.risk_flags),
                ]
            )


def write_audit(
    ranked_rows: Iterable[RankedCandidate],
    scored_by_id: Mapping[str, ScoredCandidate],
    output_path: str | Path,
) -> None:
    path = Path(output_path)
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
    good_logistics = features.country == "India" and components.logistics >= 6
    good_availability = components.availability >= 14

    if strong_evidence and good_logistics and good_availability and not risk_hits:
        return "A", "Recruiter-trustable production search/ranking fit.", ""
    if risk_hits:
        return "C", "Weak top-100 confidence due to evidence or risk flags.", "; ".join(risk_hits)
    if not moderate_evidence:
        return "B", "Plausible fit; manually review evidence depth.", "review evidence depth"
    return "B", "Plausible fit with one or more calibration concerns.", "; ".join(features.risk_flags)
