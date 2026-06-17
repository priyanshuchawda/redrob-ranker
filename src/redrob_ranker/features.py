from __future__ import annotations

import math
import re
from datetime import date, datetime
from typing import Iterable, Mapping

from .models import CandidateFeatures

PRODUCT_INDUSTRIES = {
    "AI/ML",
    "E-commerce",
    "EdTech",
    "Fintech",
    "Food Delivery",
    "Internet",
    "SaaS",
    "Software",
}

SERVICE_COMPANIES = {
    "Accenture",
    "Capgemini",
    "Cognizant",
    "Infosys",
    "Mindtree",
    "TCS",
    "Wipro",
}

TARGET_CITY_PATTERN = re.compile(
    r"\b(pune|noida|delhi|gurgaon|gurugram|ncr|mumbai|hyderabad|bangalore|bengaluru)\b",
    re.IGNORECASE,
)

RELEVANT_SKILLS = {
    "A/B Testing",
    "Airflow",
    "BM25",
    "BentoML",
    "Docker",
    "Embeddings",
    "Elasticsearch",
    "FAISS",
    "FastAPI",
    "Fine-tuning LLMs",
    "Hugging Face Transformers",
    "Information Retrieval",
    "Information Retrieval Systems",
    "Kafka",
    "Kubernetes",
    "Learning to Rank",
    "LLMs",
    "LoRA",
    "Machine Learning",
    "Milvus",
    "MLOps",
    "MLflow",
    "NLP",
    "OpenSearch",
    "Pinecone",
    "pgvector",
    "Python",
    "PyTorch",
    "Qdrant",
    "RAG",
    "Recommendation Systems",
    "Ranking Systems",
    "Scikit-learn",
    "Search Backend",
    "Semantic Search",
    "TensorFlow",
    "Text Encoders",
    "Vector Search",
    "Weaviate",
    "XGBoost",
}

RETRIEVAL_PHRASES = (
    "hybrid search",
    "semantic search",
    "embeddings-based",
    "embedding",
    "embeddings",
    "vector search",
    "vector database",
    "faiss",
    "qdrant",
    "milvus",
    "pinecone",
    "weaviate",
    "opensearch",
    "elasticsearch",
    "retrieval quality",
    "retrieval system",
    "search and discovery",
    "matching layer",
    "surface",
    "user intent",
    "relevance",
)

RANKING_PHRASES = (
    "recommendation ranking",
    "recommendation system",
    "recommendations",
    "ranking system",
    "learning to rank",
    "ranker",
    "ranking",
    "recommender",
    "matching layer",
    "explicit modeling",
    "hand-tuned heuristic",
    "heuristic system",
)

EVALUATION_PHRASES = (
    "ndcg",
    "mrr",
    "map",
    "offline evaluation",
    "evaluation",
    "a/b testing",
    "a/b test",
    "ab test",
    "relevance regression",
    "evaluation methodology",
    "online engagement",
    "offline metrics",
    "recruiter engagement",
)


def extract_features(candidate: Mapping, reference_date: date | None = None) -> CandidateFeatures:
    reference_date = reference_date or date.today()
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    history = list(candidate.get("career_history", []))
    skills = list(candidate.get("skills", []))

    current_title = str(profile.get("current_title", ""))
    location = str(profile.get("location", ""))
    country = str(profile.get("country", ""))
    years = _as_float(profile.get("years_of_experience", 0.0))
    career_text = _career_text(history)

    skill_names = tuple(str(skill.get("name", "")) for skill in skills if skill.get("name"))
    relevant_skills = tuple(sorted(name for name in skill_names if name in RELEVANT_SKILLS))
    matched_evidence = _matched_phrases(career_text)

    role_score = _role_score(current_title)
    retrieval_evidence = _count_phrases(career_text, RETRIEVAL_PHRASES)
    ranking_evidence = _count_phrases(career_text, RANKING_PHRASES)
    evaluation_evidence = _count_phrases(career_text, EVALUATION_PHRASES)
    product_months = _product_company_months(history)
    seniority_score = _seniority_score(years)
    availability_score, availability_flags = _availability_score(signals, reference_date)
    logistics_score, logistics_flags = _logistics_score(profile, signals)
    keyword_risk, keyword_flags = _keyword_risk(
        role_score=role_score,
        career_evidence=retrieval_evidence + ranking_evidence + evaluation_evidence,
        relevant_skill_count=len(relevant_skills),
        skills=skills,
    )
    domain_flags = _domain_focus_flags(profile, history, retrieval_evidence + ranking_evidence + evaluation_evidence)
    risk_flags = [*availability_flags, *logistics_flags, *keyword_flags, *domain_flags]
    risk_penalty = _risk_penalty(profile, history, signals, risk_flags, keyword_risk)

    return CandidateFeatures(
        candidate_id=str(candidate.get("candidate_id", "")),
        current_title=current_title,
        years_of_experience=years,
        location=location,
        country=country,
        role_score=role_score,
        seniority_score=seniority_score,
        retrieval_evidence=retrieval_evidence,
        ranking_evidence=ranking_evidence,
        evaluation_evidence=evaluation_evidence,
        product_company_months=product_months,
        relevant_skill_count=len(relevant_skills),
        relevant_skills=relevant_skills,
        evidence_phrases=matched_evidence,
        availability_score=availability_score,
        logistics_score=logistics_score,
        risk_penalty=risk_penalty,
        keyword_stuffing_risk=keyword_risk,
        risk_flags=tuple(dict.fromkeys(risk_flags)),
    )


def _career_text(history: Iterable[Mapping]) -> str:
    chunks: list[str] = []
    for item in history:
        chunks.append(str(item.get("title", "")))
        chunks.append(str(item.get("description", "")))
    return " ".join(chunks).lower()


def _count_phrases(text: str, phrases: Iterable[str]) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def _matched_phrases(text: str) -> tuple[str, ...]:
    phrases = [*RETRIEVAL_PHRASES, *RANKING_PHRASES, *EVALUATION_PHRASES]
    return tuple(phrase for phrase in phrases if phrase in text)


def _role_score(title: str) -> float:
    text = title.lower()
    if "junior" in text:
        if any(term in text for term in ("ml", "machine learning", "ai", "nlp", "search")):
            return 1.5
        return -1.0
    if any(term in text for term in ("marketing", "sales", "hr", "accountant", "graphic", "content")):
        return -4.0
    if any(term in text for term in ("staff machine learning", "lead ai", "senior ai", "senior machine learning")):
        return 6.5
    if any(term in text for term in ("recommendation systems", "search engineer", "applied scientist")):
        return 6.0
    if any(term in text for term in ("applied ml", "machine learning", "ml engineer", "ai engineer", "nlp engineer")):
        return 5.0
    if "data scientist" in text:
        return 4.5
    if any(term in text for term in ("software engineer", "backend engineer", "data engineer", "cloud engineer")):
        return 1.5
    return 0.0


def _seniority_score(years: float) -> float:
    if 5 <= years <= 9:
        return 5.0
    if 4 <= years < 5 or 9 < years <= 11:
        return 3.0
    if 3 <= years < 4 or 11 < years <= 14:
        return 1.0
    return -2.0


def _product_company_months(history: Iterable[Mapping]) -> int:
    return sum(
        int(item.get("duration_months") or 0)
        for item in history
        if str(item.get("industry", "")) in PRODUCT_INDUSTRIES
    )


def _availability_score(signals: Mapping, reference_date: date) -> tuple[float, list[str]]:
    flags: list[str] = []
    score = 0.0

    if bool(signals.get("open_to_work_flag")):
        score += 2.0
    else:
        flags.append("not marked open to work")

    last_active = _parse_date(signals.get("last_active_date"))
    if last_active is None:
        flags.append("missing last active date")
    else:
        inactive_days = (reference_date - last_active).days
        if inactive_days <= 30:
            score += 2.0
        elif inactive_days <= 90:
            score += 1.0
        elif inactive_days > 120:
            flags.append("stale profile")

    response_rate = _as_float(signals.get("recruiter_response_rate", 0.0))
    if response_rate >= 0.7:
        score += 2.0
    elif response_rate >= 0.5:
        score += 1.2
    elif response_rate >= 0.3:
        score += 0.5
    elif response_rate < 0.15:
        flags.append("low recruiter response")

    response_hours = _as_float(signals.get("avg_response_time_hours", 999.0))
    if response_hours <= 24:
        score += 1.2
    elif response_hours <= 72:
        score += 0.8
    elif response_hours <= 168:
        score += 0.3

    notice = int(signals.get("notice_period_days") or 0)
    if notice <= 30:
        score += 1.2
    elif notice <= 60:
        score += 0.7
    elif notice <= 90:
        score += 0.3
    elif notice >= 120:
        flags.append("long notice period")

    score += min(int(signals.get("saved_by_recruiters_30d") or 0) / 24.0, 1.0)

    if _as_float(signals.get("interview_completion_rate", 0.0)) >= 0.8:
        score += 1.0
    if _as_float(signals.get("offer_acceptance_rate", -1.0)) >= 0.5:
        score += 0.8
    if bool(signals.get("verified_email")) and bool(signals.get("verified_phone")):
        score += 0.4

    return min(score, 10.0), flags


def _logistics_score(profile: Mapping, signals: Mapping) -> tuple[float, list[str]]:
    score = 0.0
    flags: list[str] = []
    location = str(profile.get("location", ""))
    country = str(profile.get("country", ""))

    if country == "India":
        score += 2.0
    else:
        flags.append("outside India")
        return (1.0 if bool(signals.get("willing_to_relocate")) else 0.0), flags

    if TARGET_CITY_PATTERN.search(location):
        score += 2.0
    elif bool(signals.get("willing_to_relocate")):
        score += 1.0

    if str(signals.get("preferred_work_mode", "")) in {"hybrid", "flexible", "onsite"}:
        score += 1.0
    if bool(signals.get("willing_to_relocate")):
        score += 1.0

    return score, flags


def _keyword_risk(
    *,
    role_score: float,
    career_evidence: int,
    relevant_skill_count: int,
    skills: Iterable[Mapping],
) -> tuple[bool, list[str]]:
    flags: list[str] = []
    expert_zero = sum(
        1
        for skill in skills
        if skill.get("proficiency") == "expert" and int(skill.get("duration_months") or 0) == 0
    )
    if expert_zero >= 5:
        flags.append("expert skills with zero duration")
    keyword_risk = (relevant_skill_count >= 6 and career_evidence <= 1 and role_score < 1) or expert_zero >= 5
    if keyword_risk:
        flags.append("keyword-stuffed profile")
    return keyword_risk, flags


def _risk_penalty(
    profile: Mapping,
    history: Iterable[Mapping],
    signals: Mapping,
    risk_flags: list[str],
    keyword_risk: bool,
) -> float:
    penalty = 0.0
    if keyword_risk:
        penalty += 25.0
    if "stale profile" in risk_flags:
        penalty += 8.0
    if "low recruiter response" in risk_flags:
        penalty += 6.0
    if "long notice period" in risk_flags:
        penalty += 3.0
    if str(profile.get("current_company", "")) in SERVICE_COMPANIES:
        penalty += 4.0
    if str(profile.get("current_industry", "")) in {"IT Services", "Consulting"}:
        penalty += 3.0
    if _experience_history_gap(profile, history) > 3.0:
        penalty += 20.0
    if "outside India" in risk_flags:
        penalty += 12.0
    if "not marked open to work" in risk_flags:
        penalty += 6.0
    if "non-target ML domain" in risk_flags:
        penalty += 12.0
    if _as_float(signals.get("github_activity_score", 0.0)) == -1:
        penalty += 0.5
    return penalty


def _domain_focus_flags(profile: Mapping, history: Iterable[Mapping], target_evidence: int) -> list[str]:
    text = " ".join(
        [
            str(profile.get("headline", "")),
            str(profile.get("summary", "")),
            _career_text(history),
        ]
    ).lower()
    non_target_terms = (
        "computer vision",
        "image classification",
        "object detection",
        "speech recognition",
        "robotics",
        "tts",
        "asr",
    )
    transition_terms = (
        "interested in transitioning",
        "transitioning toward",
        "professional experience there is limited",
        "production deployment was handled",
    )
    if (
        any(term in text for term in non_target_terms)
        and any(term in text for term in transition_terms)
        and target_evidence <= 2
    ):
        return ["non-target ML domain"]
    return []


def _experience_history_gap(profile: Mapping, history: Iterable[Mapping]) -> float:
    stated_years = _as_float(profile.get("years_of_experience", 0.0))
    months = sum(int(item.get("duration_months") or 0) for item in history)
    if months <= 0:
        return 0.0
    return abs(stated_years - months / 12.0)


def _parse_date(value: object) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def _as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(number) or math.isinf(number):
        return 0.0
    return number
