from __future__ import annotations

import math
from typing import Mapping


def evaluate_payload(payload: Mapping, labels: Mapping[str, int] | None = None, top_n: int = 10) -> dict:
    rankings = list(payload.get("rankings", []))
    top_n = min(top_n, len(rankings)) if rankings else top_n
    if labels:
        return _evaluate_with_labels(rankings, labels, top_n)
    return _proxy_evaluation(rankings, top_n)


def render_evaluation_report(result: Mapping) -> str:
    lines = [
        "# Evaluation Report",
        "",
        f"Mode: {result.get('mode')}",
        f"Metric label: {result.get('metric_label')}",
        "",
        "## Metrics",
        "",
    ]
    for key, value in result.get("metrics", {}).items():
        lines.append(f"- {key}: {value}")
    if result.get("notes"):
        lines.extend(["", "## Notes", ""])
        for note in result["notes"]:
            lines.append(f"- {note}")
    return "\n".join(lines).strip() + "\n"


def _evaluate_with_labels(rankings: list[Mapping], labels: Mapping[str, int], top_n: int) -> dict:
    ordered_ids = [str(row.get("candidate_id")) for row in rankings]
    top_ids = ordered_ids[:top_n]
    positives = {candidate_id for candidate_id, label in labels.items() if int(label) > 0}
    true_positives = [candidate_id for candidate_id in top_ids if candidate_id in positives]
    false_positives = [candidate_id for candidate_id in top_ids if candidate_id not in positives]
    false_negatives = [candidate_id for candidate_id in positives if candidate_id not in top_ids]
    precision = len(true_positives) / top_n if top_n else 0.0
    recall = len(true_positives) / len(positives) if positives else 0.0
    relevances = [int(labels.get(candidate_id, 0)) for candidate_id in ordered_ids]
    ideal = sorted((int(value) for value in labels.values()), reverse=True)
    ndcg = _dcg(relevances, top_n) / _dcg(ideal, top_n) if _dcg(ideal, top_n) else 0.0
    mrr = 0.0
    for index, candidate_id in enumerate(ordered_ids, start=1):
        if candidate_id in positives:
            mrr = 1 / index
            break
    return {
        "mode": "labeled",
        "metric_label": "real labels supplied",
        "metrics": {
            "precision_at_k": round(precision, 4),
            "recall_at_k": round(recall, 4),
            "ndcg_at_k": round(ndcg, 4),
            "mrr": round(mrr, 4),
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        },
        "notes": ["Metrics use caller-supplied labels."],
    }


def _proxy_evaluation(rankings: list[Mapping], top_n: int) -> dict:
    top = rankings[:top_n]
    high_risk = sum(1 for row in top if float(row.get("risk_score", 0) or 0) >= 50)
    strong_proof = sum(1 for row in top if float(row.get("proof_score", 0) or 0) >= 50)
    missing_evidence = sum(1 for row in top if row.get("missing_evidence"))
    return {
        "mode": "proxy",
        "metric_label": "synthetic/proxy metrics, not real recruiter accuracy",
        "metrics": {
            "top_k": top_n,
            "high_risk_profiles_in_top_k": high_risk,
            "strong_proof_profiles_in_top_k": strong_proof,
            "profiles_with_missing_evidence_in_top_k": missing_evidence,
            "deterministic_sort_check": _deterministic_sort_check(rankings),
        },
        "notes": [
            "No ground-truth labels were supplied.",
            "These proxy checks evaluate consistency and risk behavior, not real hiring accuracy.",
        ],
    }


def _deterministic_sort_check(rankings: list[Mapping]) -> bool:
    ranks = [int(row.get("rank", 0)) for row in rankings]
    return ranks == list(range(1, len(ranks) + 1))


def _dcg(relevances: list[int], cutoff: int) -> float:
    return sum((2**rel - 1) / math.log2(index + 2) for index, rel in enumerate(relevances[:cutoff]))

