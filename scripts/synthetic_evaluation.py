from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from redrob_ranker.scoring import rank_scored_candidates, score_candidates  # noqa: E402


REFERENCE_DATE = date(2026, 6, 17)


@dataclass(frozen=True)
class SyntheticCase:
    candidate: dict
    archetype: str
    relevance: int
    should_shortlist: bool


def _base(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "profile": {
            "headline": "Software Engineer",
            "summary": "Builds software systems.",
            "location": "Pune, Maharashtra",
            "country": "India",
            "years_of_experience": 7.0,
            "current_title": "Software Engineer",
            "current_company": "ProductCo",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "company": "ProductCo",
                "title": "Software Engineer",
                "duration_months": 48,
                "is_current": True,
                "industry": "Software",
                "description": "Built reliable Python backend APIs for a product team.",
            },
            {
                "company": "StartupCo",
                "title": "Software Engineer",
                "duration_months": 36,
                "is_current": False,
                "industry": "SaaS",
                "description": "Developed data pipelines and internal services.",
            },
        ],
        "skills": [
            {"name": "Python", "proficiency": "advanced", "endorsements": 20, "duration_months": 60},
            {"name": "Docker", "proficiency": "intermediate", "endorsements": 10, "duration_months": 30},
        ],
        "redrob_signals": {
            "last_active_date": "2026-06-10",
            "open_to_work_flag": True,
            "recruiter_response_rate": 0.75,
            "avg_response_time_hours": 20,
            "notice_period_days": 30,
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": True,
            "saved_by_recruiters_30d": 15,
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.65,
            "verified_email": True,
            "verified_phone": True,
            "skill_assessment_scores": {"Python": 88},
        },
    }


def _strong_search(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Senior AI Engineer | Search relevance and ranking",
            "summary": "Production ML engineer specializing in retrieval and ranking systems.",
            "current_title": rng.choice(
                ["Senior AI Engineer", "Senior Machine Learning Engineer", "Search Relevance Engineer"]
            ),
            "current_company": rng.choice(["Freshworks", "Meesho", "Razorpay", "ProductAI"]),
            "current_industry": rng.choice(["SaaS", "E-commerce", "Fintech", "AI/ML"]),
            "years_of_experience": rng.uniform(5.2, 9.0),
        }
    )
    row["career_history"][0].update(
        {
            "title": row["profile"]["current_title"],
            "industry": row["profile"]["current_industry"],
            "description": (
                "Owned and shipped a production two-tower candidate generation service, "
                "hybrid semantic search, and cross encoder reranking. Improved NDCG by "
                f"{rng.randint(8, 24)}% and reduced serving latency by {rng.randint(15, 45)}%. "
                "Led offline evaluation and A/B testing."
            ),
        }
    )
    row["career_history"][1]["description"] = (
        "Built vector search and recommendation services with Python, FAISS, Docker, and FastAPI."
    )
    row["skills"].extend(
        [
            {"name": "Vector Search", "proficiency": "advanced", "endorsements": 25, "duration_months": 36},
            {"name": "Learning to Rank", "proficiency": "advanced", "endorsements": 18, "duration_months": 30},
            {"name": "Cross Encoder", "proficiency": "advanced", "endorsements": 15, "duration_months": 24},
            {"name": "Two-Tower Models", "proficiency": "advanced", "endorsements": 16, "duration_months": 30},
            {"name": "MLOps", "proficiency": "advanced", "endorsements": 18, "duration_months": 30},
        ]
    )
    return SyntheticCase(row, "strong_search", 4, True)


def _plain_language_fit(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Lead ML Engineer building relevance products",
            "summary": "Connects users to the most useful results through product ML.",
            "current_title": "Lead AI Engineer",
            "current_industry": "AI/ML",
            "years_of_experience": rng.uniform(6.0, 9.0),
        }
    )
    row["career_history"][0].update(
        {
            "title": "Lead AI Engineer",
            "industry": "AI/ML",
            "description": (
                "Owned the search and discovery experience end-to-end. Designed the matching "
                "layer that decides what to surface for each user intent, replaced hand-tuned "
                "heuristics with explicit modeling, and tied evaluation methodology to online engagement."
            ),
        }
    )
    row["skills"].extend(
        [
            {"name": "Information Retrieval Systems", "proficiency": "advanced", "endorsements": 16, "duration_months": 30},
            {"name": "Ranking Systems", "proficiency": "advanced", "endorsements": 15, "duration_months": 30},
        ]
    )
    return SyntheticCase(row, "plain_language_fit", 4, True)


def _strong_but_unavailable(candidate_id: str, rng: random.Random) -> SyntheticCase:
    case = _strong_search(candidate_id, rng)
    row = deepcopy(case.candidate)
    row["redrob_signals"].update(
        {
            "last_active_date": "2025-09-01",
            "open_to_work_flag": False,
            "recruiter_response_rate": 0.05,
            "avg_response_time_hours": 300,
            "notice_period_days": 150,
            "saved_by_recruiters_30d": 0,
        }
    )
    return SyntheticCase(row, "strong_but_unavailable", 3, False)


def _profile_only_claims(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Senior AI Engineer | RAG | Semantic Search | Ranking",
            "summary": (
                "Claims hybrid search, candidate matching, learning-to-rank, cross encoder "
                "reranking, NDCG, and A/B testing."
            ),
            "current_title": "Senior AI Engineer",
            "years_of_experience": rng.uniform(5.0, 9.0),
        }
    )
    row["career_history"][0]["description"] = "Built Python APIs and data pipelines for internal teams."
    row["career_history"][1]["description"] = "Maintained backend services."
    row["skills"].extend(
        [
            {"name": "RAG", "proficiency": "advanced", "endorsements": 5, "duration_months": 8},
            {"name": "Vector Search", "proficiency": "intermediate", "endorsements": 3, "duration_months": 8},
        ]
    )
    return SyntheticCase(row, "profile_only_claims", 2, False)


def _generic_llm_demo(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "AI Specialist | OpenAI LangChain RAG Pinecone",
            "summary": "Built tutorials, templates, demos, and proof-of-concept chatbots.",
            "current_title": "AI Specialist",
            "years_of_experience": rng.uniform(4.0, 8.0),
        }
    )
    row["career_history"] = [
        {
            "company": "ConsultCo",
            "title": "AI Specialist",
            "duration_months": 18,
            "is_current": True,
            "industry": "Consulting",
            "description": (
                "Built LangChain, OpenAI, RAG, and Pinecone demos and tutorials. "
                "No production retrieval, ranking, evaluation, or serving ownership."
            ),
        }
    ]
    row["skills"] = [
        {"name": name, "proficiency": "expert", "endorsements": 2, "duration_months": 5}
        for name in ["LLMs", "RAG", "Pinecone", "Fine-tuning LLMs", "LoRA"]
    ]
    return SyntheticCase(row, "generic_llm_demo", 0, False)


def _keyword_stuffer(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Marketing Manager | AI ML RAG Search",
            "current_title": "Marketing Manager",
            "current_industry": "Manufacturing",
            "years_of_experience": rng.uniform(5.0, 10.0),
        }
    )
    row["career_history"] = [
        {
            "company": "BrandCo",
            "title": "Marketing Manager",
            "duration_months": 80,
            "is_current": True,
            "industry": "Manufacturing",
            "description": "Led campaigns, vendors, content, and brand strategy.",
        }
    ]
    row["skills"] = [
        {"name": name, "proficiency": "expert", "endorsements": 0, "duration_months": 0}
        for name in [
            "LLMs",
            "RAG",
            "Pinecone",
            "FAISS",
            "Vector Search",
            "Embeddings",
            "Machine Learning",
            "NLP",
        ]
    ]
    return SyntheticCase(row, "keyword_stuffer", 0, False)


def _non_target_ml(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "AI Research Engineer | Computer Vision and Speech",
            "summary": "Computer vision and speech specialist interested in transitioning to retrieval.",
            "current_title": "AI Research Engineer",
            "current_industry": "AI/ML",
            "years_of_experience": rng.uniform(5.0, 9.0),
        }
    )
    row["career_history"][0].update(
        {
            "title": "AI Research Engineer",
            "industry": "AI/ML",
            "description": (
                "Built image classification, object detection, and speech recognition models. "
                "Production deployment was handled by another team; transitioning toward NLP and retrieval."
            ),
        }
    )
    row["skills"] = [
        {"name": "Machine Learning", "proficiency": "expert", "endorsements": 30, "duration_months": 60},
        {"name": "NLP", "proficiency": "beginner", "endorsements": 3, "duration_months": 4},
    ]
    return SyntheticCase(row, "non_target_ml", 1, False)


def _backend_adjacent(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Senior Backend Engineer | Python platforms",
            "current_title": "Senior Backend Engineer",
            "years_of_experience": rng.uniform(5.0, 9.0),
        }
    )
    row["career_history"][0]["description"] = (
        "Owned scalable Python APIs, Kafka pipelines, Kubernetes deployments, monitoring, "
        "and low-latency services. Partnered with ML teams but did not own ranking models."
    )
    row["skills"].extend(
        [
            {"name": "Kafka", "proficiency": "advanced", "endorsements": 18, "duration_months": 36},
            {"name": "Kubernetes", "proficiency": "advanced", "endorsements": 16, "duration_months": 30},
            {"name": "FastAPI", "proficiency": "advanced", "endorsements": 20, "duration_months": 36},
        ]
    )
    return SyntheticCase(row, "backend_adjacent", 2, False)


def _junior_retrieval(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _strong_search(candidate_id, rng).candidate
    row["profile"].update(
        {
            "headline": "Junior ML Engineer | Search",
            "current_title": "Junior ML Engineer",
            "years_of_experience": rng.uniform(1.0, 2.5),
        }
    )
    row["career_history"] = [row["career_history"][0]]
    row["career_history"][0]["duration_months"] = 18
    return SyntheticCase(row, "junior_retrieval", 2, False)


def _outside_india_fit(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _strong_search(candidate_id, rng).candidate
    row["profile"].update({"location": "London", "country": "United Kingdom"})
    row["redrob_signals"]["willing_to_relocate"] = False
    return SyntheticCase(row, "outside_india_fit", 3, False)


def _missing_telemetry_fit(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _strong_search(candidate_id, rng).candidate
    row["redrob_signals"] = {}
    return SyntheticCase(row, "missing_telemetry_fit", 3, True)


def _negated_claims(candidate_id: str, rng: random.Random) -> SyntheticCase:
    row = _base(candidate_id)
    row["profile"].update(
        {
            "headline": "Senior Software Engineer exploring AI",
            "current_title": "Senior Software Engineer",
            "years_of_experience": rng.uniform(5.0, 9.0),
        }
    )
    row["career_history"][0]["description"] = (
        "Built backend APIs. No production semantic search, candidate matching, ranking, "
        "recommendation, retrieval evaluation, or A/B testing ownership."
    )
    return SyntheticCase(row, "negated_claims", 0, False)


FACTORIES = {
    "strong_search": _strong_search,
    "plain_language_fit": _plain_language_fit,
    "strong_but_unavailable": _strong_but_unavailable,
    "profile_only_claims": _profile_only_claims,
    "generic_llm_demo": _generic_llm_demo,
    "keyword_stuffer": _keyword_stuffer,
    "non_target_ml": _non_target_ml,
    "backend_adjacent": _backend_adjacent,
    "junior_retrieval": _junior_retrieval,
    "outside_india_fit": _outside_india_fit,
    "missing_telemetry_fit": _missing_telemetry_fit,
    "negated_claims": _negated_claims,
}


def generate_cases(per_archetype: int, seed: int) -> list[SyntheticCase]:
    rng = random.Random(seed)
    cases: list[SyntheticCase] = []
    counter = 1
    for archetype, factory in FACTORIES.items():
        for _ in range(per_archetype):
            candidate_id = f"SYN_{counter:07d}"
            cases.append(factory(candidate_id, rng))
            counter += 1
    rng.shuffle(cases)
    return cases


def _dcg(relevances: list[int], cutoff: int) -> float:
    import math

    return sum((2**rel - 1) / math.log2(index + 2) for index, rel in enumerate(relevances[:cutoff]))


def evaluate(cases: list[SyntheticCase], top_n: int) -> tuple[dict, list[dict]]:
    labels = {case.candidate["candidate_id"]: case for case in cases}
    scored = score_candidates((case.candidate for case in cases), reference_date=REFERENCE_DATE)
    ranked = rank_scored_candidates(scored, top_n=len(scored))
    scored_by_id = {row.candidate_id: row for row in scored}

    ordered_labels = [labels[row.candidate_id] for row in ranked]
    shortlist = ordered_labels[:top_n]
    positives = sum(case.should_shortlist for case in cases)
    true_positives = sum(case.should_shortlist for case in shortlist)
    precision = true_positives / top_n
    recall = true_positives / positives

    relevances = [case.relevance for case in ordered_labels]
    ideal = sorted((case.relevance for case in cases), reverse=True)
    ndcg = _dcg(relevances, top_n) / _dcg(ideal, top_n)

    reciprocal_ranks = []
    for case in cases:
        if case.should_shortlist:
            rank = next(index for index, row in enumerate(ranked, start=1) if row.candidate_id == case.candidate["candidate_id"])
            reciprocal_ranks.append(1 / rank)

    archetype_scores: dict[str, list[float]] = defaultdict(list)
    archetype_ranks: dict[str, list[int]] = defaultdict(list)
    details: list[dict] = []
    for rank, row in enumerate(ranked, start=1):
        case = labels[row.candidate_id]
        archetype_scores[case.archetype].append(row.score)
        archetype_ranks[case.archetype].append(rank)
        details.append(
            {
                "rank": rank,
                "candidate_id": row.candidate_id,
                "archetype": case.archetype,
                "relevance": case.relevance,
                "should_shortlist": case.should_shortlist,
                "score": row.score,
                "reasoning": row.reasoning,
                "risk_flags": "; ".join(scored_by_id[row.candidate_id].features.risk_flags),
            }
        )

    top_mix = Counter(case.archetype for case in shortlist)
    false_positives = [row for row in details[:top_n] if not row["should_shortlist"]]
    false_negatives = [row for row in details[top_n:] if row["should_shortlist"]]
    metrics = {
        "candidates": len(cases),
        "top_n": top_n,
        "positives": positives,
        "precision_at_n": precision,
        "recall_at_n": recall,
        "ndcg_at_n": ndcg,
        "mean_reciprocal_rank_of_positives": mean(reciprocal_ranks),
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "top_mix": dict(top_mix),
        "archetypes": {
            name: {
                "mean_score": mean(archetype_scores[name]),
                "best_rank": min(archetype_ranks[name]),
                "worst_rank": max(archetype_ranks[name]),
            }
            for name in FACTORIES
        },
    }
    return metrics, details


def write_outputs(metrics: dict, details: list[dict], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    with (output_dir / "ranking.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a labeled synthetic ranking evaluation.")
    parser.add_argument("--per-archetype", type=int, default=25)
    parser.add_argument("--top-n", type=int, default=75)
    parser.add_argument("--seed", type=int, default=20260617)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".synthetic-eval")
    args = parser.parse_args()

    cases = generate_cases(args.per_archetype, args.seed)
    metrics, details = evaluate(cases, top_n=args.top_n)
    write_outputs(metrics, details, args.output_dir)

    print(json.dumps(metrics, indent=2))
    print("\nTop 10:")
    for row in details[:10]:
        print(
            f"{row['rank']:>3} {row['archetype']:<26} "
            f"rel={row['relevance']} score={row['score']:.2f}"
        )
    print(f"\nWrote evaluation artifacts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
