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
    "Two-Tower Models",
    "Cross Encoder",
    "Reranking",
    "Vector Search",
    "Weaviate",
    "XGBoost",
}

SKILL_ALIASES = {
    "ab testing": "A/B Testing",
    "a b testing": "A/B Testing",
    "cross-encoder": "Cross Encoder",
    "cross encoders": "Cross Encoder",
    "finetuning llms": "Fine-tuning LLMs",
    "fine tuning llms": "Fine-tuning LLMs",
    "huggingface transformers": "Hugging Face Transformers",
    "information retrieval system": "Information Retrieval Systems",
    "learning-to-rank": "Learning to Rank",
    "large language models": "LLMs",
    "ml ops": "MLOps",
    "open search": "OpenSearch",
    "postgres vector": "pgvector",
    "recommendation system": "Recommendation Systems",
    "recommender systems": "Recommendation Systems",
    "ranking system": "Ranking Systems",
    "re-ranking": "Reranking",
    "semantic-search": "Semantic Search",
    "two tower models": "Two-Tower Models",
    "two-tower model": "Two-Tower Models",
    "vector-search": "Vector Search",
}

SKILL_LOOKUP = {re.sub(r"[^a-z0-9]+", " ", skill.casefold()).strip(): skill for skill in RELEVANT_SKILLS}
SKILL_LOOKUP.update(
    {
        re.sub(r"[^a-z0-9]+", " ", alias.casefold()).strip(): canonical
        for alias, canonical in SKILL_ALIASES.items()
    }
)

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
    "candidate matching",
    "talent matching",
    "job matching",
    "entity matching",
    "profile matching",
    "candidate generation",
    "recall stage",
    "search relevance",
    "two-tower",
    "two tower",
    "retrieval evaluation",
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
    "learning-to-rank",
    "ranking model",
    "reranker",
    "reranking",
    "cross encoder",
    "precision stage",
    "candidate recommendation",
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
    "retrieval evaluation",
)

ALL_EVIDENCE_PHRASES = tuple(
    dict.fromkeys((*RETRIEVAL_PHRASES, *RANKING_PHRASES, *EVALUATION_PHRASES))
)

EVIDENCE_CONCEPTS: dict[str, dict[str, tuple[str, ...]]] = {
    "retrieval": {
        "hybrid/semantic search": ("hybrid search", "semantic search", "vector search"),
        "dense representations": ("embedding", "embeddings", "text encoder"),
        "retrieval infrastructure": (
            "faiss",
            "qdrant",
            "milvus",
            "pinecone",
            "weaviate",
            "opensearch",
            "elasticsearch",
            "vector database",
        ),
        "information retrieval": ("information retrieval", "retrieval system", "retrieval quality"),
        "matching systems": (
            "matching layer",
            "candidate matching",
            "talent matching",
            "job matching",
            "entity matching",
            "profile matching",
        ),
        "candidate generation": ("candidate generation", "recall stage"),
        "search relevance": ("search relevance", "search and discovery", "user intent", "relevance"),
        "dual encoder retrieval": ("two-tower", "two tower", "dual encoder"),
    },
    "ranking": {
        "learning to rank": ("learning to rank", "learning-to-rank", "ranking model"),
        "reranking": ("reranker", "reranking", "cross encoder", "precision stage"),
        "recommendations": (
            "recommendation ranking",
            "recommendation system",
            "recommendations",
            "recommender",
            "candidate recommendation",
        ),
        "ranking systems": ("ranking system", "ranker", "ranking"),
        "matching policy": ("matching layer", "explicit modeling"),
        "ranking heuristics": ("hand-tuned heuristic", "heuristic system"),
    },
    "evaluation": {
        "ranking metrics": ("ndcg", "mrr", "mean reciprocal rank", "mean average precision"),
        "offline evaluation": ("offline evaluation", "offline metrics", "retrieval evaluation"),
        "online experiments": ("a/b testing", "a/b test", "ab test", "online experiment"),
        "relevance quality": ("relevance regression", "retrieval quality"),
        "product outcomes": ("online engagement", "recruiter engagement"),
        "evaluation methodology": ("evaluation methodology",),
    },
}

PRODUCTION_TERMS = (
    "shipped",
    "production",
    "deployed",
    "serving",
    "launched",
    "operationalized",
    "scaled",
    "end-to-end",
    "end to end",
)

OWNERSHIP_TERMS = (
    "owned",
    "led",
    "designed",
    "architected",
    "built",
    "implemented",
    "developed",
)

ENGINEERING_TERMS = (
    "api",
    "backend",
    "pipeline",
    "latency",
    "throughput",
    "monitoring",
    "mlops",
    "docker",
    "kubernetes",
    "airflow",
    "kafka",
    "fastapi",
    "model serving",
    "feature store",
    "ci/cd",
)

LEADERSHIP_TERMS = (
    "tech lead",
    "team lead",
    "led a team",
    "mentored",
    "managed engineers",
    "hired",
    "grew the team",
    "founding engineer",
    "staff engineer",
    "principal engineer",
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
    profile_text = _profile_text(profile)

    skill_names = tuple(str(skill.get("name", "")) for skill in skills if skill.get("name"))
    relevant_skills = tuple(
        sorted(
            {
                canonical
                for name in skill_names
                if (canonical := _canonical_skill(name)) is not None
            }
        )
    )
    career_matches = _matching_phrases(career_text)
    profile_matches = _matching_phrases(profile_text)
    matched_evidence = tuple(
        phrase
        for phrase in ALL_EVIDENCE_PHRASES
        if phrase in career_matches or phrase in profile_matches
    )

    role_score = _role_score(current_title)
    retrieval_evidence = sum(phrase in career_matches for phrase in RETRIEVAL_PHRASES)
    ranking_evidence = sum(phrase in career_matches for phrase in RANKING_PHRASES)
    evaluation_evidence = sum(phrase in career_matches for phrase in EVALUATION_PHRASES)
    profile_retrieval_evidence = sum(phrase in profile_matches for phrase in RETRIEVAL_PHRASES)
    profile_ranking_evidence = sum(phrase in profile_matches for phrase in RANKING_PHRASES)
    profile_evaluation_evidence = sum(phrase in profile_matches for phrase in EVALUATION_PHRASES)
    career_evidence_score = float(retrieval_evidence + ranking_evidence + evaluation_evidence)
    profile_evidence_score = 0.5 * float(
        profile_retrieval_evidence + profile_ranking_evidence + profile_evaluation_evidence
    )
    quality_scores, evidence_concepts = _career_evidence_quality(history)
    production_score = _production_score(history)
    engineering_score = _engineering_score(history, relevant_skills)
    leadership_score = _leadership_score(profile, history)
    product_months = _product_company_months(history)
    seniority_score = _seniority_score(years, current_title)
    availability_score, availability_flags = _availability_score(signals, reference_date)
    logistics_score, logistics_flags = _logistics_score(profile, signals)
    keyword_risk, keyword_flags = _keyword_risk(
        role_score=role_score,
        career_evidence=retrieval_evidence + ranking_evidence + evaluation_evidence,
        relevant_skill_count=len(relevant_skills),
        skills=skills,
    )
    career_evidence = retrieval_evidence + ranking_evidence + evaluation_evidence
    skill_trust_score = _skill_trust_score(skills, signals, career_evidence)
    evidence_confidence = _evidence_confidence(
        quality_scores=quality_scores,
        production_score=production_score,
        engineering_score=engineering_score,
        relevant_skills=relevant_skills,
        career_text=career_text,
    )
    domain_flags = _domain_focus_flags(profile, history, career_evidence)
    generic_ai_flags = _generic_ai_flags(profile, history, skills, career_evidence)
    risk_flags = [*availability_flags, *logistics_flags, *keyword_flags, *domain_flags, *generic_ai_flags]
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
        profile_retrieval_evidence=profile_retrieval_evidence,
        profile_ranking_evidence=profile_ranking_evidence,
        profile_evaluation_evidence=profile_evaluation_evidence,
        career_evidence_score=career_evidence_score,
        profile_evidence_score=profile_evidence_score,
        retrieval_quality_score=round(quality_scores["retrieval"], 6),
        ranking_quality_score=round(quality_scores["ranking"], 6),
        evaluation_quality_score=round(quality_scores["evaluation"], 6),
        production_score=round(production_score, 6),
        engineering_score=round(engineering_score, 6),
        leadership_score=round(leadership_score, 6),
        evidence_confidence=round(evidence_confidence, 6),
        product_company_months=product_months,
        relevant_skill_count=len(relevant_skills),
        skill_trust_score=round(skill_trust_score, 6),
        relevant_skills=relevant_skills,
        evidence_phrases=matched_evidence,
        evidence_concepts=evidence_concepts,
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


def _profile_text(profile: Mapping) -> str:
    return " ".join(
        [
            str(profile.get("headline", "")),
            str(profile.get("summary", "")),
            str(profile.get("current_title", "")),
        ]
    ).lower()


def _canonical_skill(name: str) -> str | None:
    key = re.sub(r"[^a-z0-9]+", " ", name.casefold()).strip()
    return SKILL_LOOKUP.get(key)


def _matching_phrases(text: str) -> set[str]:
    return {phrase for phrase in ALL_EVIDENCE_PHRASES if _has_phrase(text, phrase)}


def _has_phrase(text: str, phrase: str) -> bool:
    phrase = phrase.lower()
    start = text.find(phrase)
    while start != -1:
        before = start - 1
        after = start + len(phrase)
        has_left_boundary = before < 0 or not text[before].isalnum()
        has_right_boundary = after >= len(text) or not text[after].isalnum()
        if has_left_boundary and has_right_boundary and not _is_negated(text, start):
            return True
        start = text.find(phrase, start + 1)
    return False


def _is_negated(text: str, start: int) -> bool:
    clause_start = max(
        text.rfind(".", 0, start),
        text.rfind(";", 0, start),
        text.rfind("!", 0, start),
        text.rfind("?", 0, start),
    )
    prefix = text[max(clause_start + 1, start - 70) : start]
    return bool(
        re.search(
            r"\b(no|not|without|lacks?|lacking|limited|little|never|neither)\b[^.;!?]{0,55}$",
            prefix,
        )
    )


def _career_evidence_quality(history: Iterable[Mapping]) -> tuple[dict[str, float], tuple[str, ...]]:
    scores = {category: 0.0 for category in EVIDENCE_CONCEPTS}
    concepts: list[str] = []
    history_items = list(history)

    for index, item in enumerate(history_items):
        text = " ".join([str(item.get("title", "")), str(item.get("description", ""))]).lower()
        is_current = bool(item.get("is_current")) or index == 0
        recency_weight = 1.0 if is_current else max(0.55, 0.82 - index * 0.08)
        production_context = 1.15 if any(_has_phrase(text, term) for term in PRODUCTION_TERMS) else 1.0

        for category, category_concepts in EVIDENCE_CONCEPTS.items():
            for concept, phrases in category_concepts.items():
                if any(_has_phrase(text, phrase) for phrase in phrases):
                    scores[category] += recency_weight * production_context
                    if concept not in concepts:
                        concepts.append(concept)

    return scores, tuple(concepts)


def _production_score(history: Iterable[Mapping]) -> float:
    score = 0.0
    for index, item in enumerate(history):
        text = str(item.get("description", "")).lower()
        recency_weight = 1.0 if bool(item.get("is_current")) or index == 0 else max(0.55, 0.82 - index * 0.08)
        production_hits = sum(1 for term in PRODUCTION_TERMS if _has_phrase(text, term))
        ownership_hits = sum(1 for term in OWNERSHIP_TERMS if _has_phrase(text, term))
        impact_hits = len(re.findall(r"\b(?:improved|increased|reduced|cut|grew|lifted|saved)\b", text))
        metric_hits = len(re.findall(r"\b\d+(?:\.\d+)?\s*(?:%|ms|x\b|million|k\b)", text))
        score += recency_weight * (
            min(production_hits, 3) * 0.9
            + min(ownership_hits, 3) * 0.55
            + min(impact_hits + metric_hits, 3) * 0.45
        )
    return min(score, 8.0)


def _engineering_score(history: Iterable[Mapping], relevant_skills: tuple[str, ...]) -> float:
    text = _career_text(history)
    evidence = sum(1 for term in ENGINEERING_TERMS if _has_phrase(text, term))
    deployment_skills = {
        "Airflow",
        "BentoML",
        "Docker",
        "FastAPI",
        "Kafka",
        "Kubernetes",
        "MLflow",
        "MLOps",
    }
    skill_hits = len(deployment_skills.intersection(relevant_skills))
    return min(evidence * 0.7 + skill_hits * 0.45, 6.0)


def _leadership_score(profile: Mapping, history: Iterable[Mapping]) -> float:
    text = " ".join(
        [
            str(profile.get("current_title", "")),
            str(profile.get("headline", "")),
            _career_text(history),
        ]
    ).lower()
    return min(sum(1 for term in LEADERSHIP_TERMS if _has_phrase(text, term)) * 0.8, 4.0)


def _evidence_confidence(
    *,
    quality_scores: Mapping[str, float],
    production_score: float,
    engineering_score: float,
    relevant_skills: tuple[str, ...],
    career_text: str,
) -> float:
    core_quality = quality_scores["retrieval"] + quality_scores["ranking"] + quality_scores["evaluation"]
    skill_groups = {
        "retrieval": {
            "BM25",
            "Embeddings",
            "FAISS",
            "Information Retrieval",
            "Information Retrieval Systems",
            "Semantic Search",
            "Vector Search",
        },
        "ranking": {
            "Cross Encoder",
            "Learning to Rank",
            "Ranking Systems",
            "Recommendation Systems",
            "Reranking",
            "Two-Tower Models",
        },
        "engineering": {"Docker", "FastAPI", "Kubernetes", "MLOps", "Python"},
    }
    corroborated_groups = 0
    if quality_scores["retrieval"] > 0 and skill_groups["retrieval"].intersection(relevant_skills):
        corroborated_groups += 1
    if quality_scores["ranking"] > 0 and skill_groups["ranking"].intersection(relevant_skills):
        corroborated_groups += 1
    if engineering_score > 0 and skill_groups["engineering"].intersection(relevant_skills):
        corroborated_groups += 1
    detailed_history = min(len(career_text.split()) / 120.0, 1.5)
    return min(core_quality * 0.22 + production_score * 0.28 + corroborated_groups * 0.7 + detailed_history, 6.0)


def _role_score(title: str) -> float:
    text = title.lower()
    if "junior" in text:
        if any(term in text for term in ("ml", "machine learning", "ai", "nlp", "search")):
            return 1.5
        return -1.0
    if any(term in text for term in ("marketing", "sales", "hr", "accountant", "graphic", "content")):
        return -4.0
    if any(
        term in text
        for term in (
            "founding ai engineer",
            "founding machine learning engineer",
            "staff ai engineer",
            "principal ai engineer",
            "relevance engineer",
            "search relevance engineer",
            "ranking engineer",
            "recommendation engineer",
            "machine learning scientist",
        )
    ):
        return 6.5
    if any(term in text for term in ("ml platform engineer", "applied ai engineer")):
        return 5.8
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


def _seniority_score(years: float, title: str = "") -> float:
    if 5 <= years <= 9:
        return 5.0
    if 4 <= years < 5 or 9 < years <= 12:
        return 3.0
    if 3 <= years < 4:
        return 1.0
    if years > 12 and any(term in title.casefold() for term in ("staff", "principal", "lead", "architect")):
        return 2.0
    return -2.0


def _product_company_months(history: Iterable[Mapping]) -> int:
    product_industries = {industry.casefold() for industry in PRODUCT_INDUSTRIES}
    return sum(
        int(item.get("duration_months") or 0)
        for item in history
        if str(item.get("industry", "")).casefold() in product_industries
    )


def _availability_score(signals: Mapping, reference_date: date) -> tuple[float, list[str]]:
    flags: list[str] = []
    score = 0.0

    if "open_to_work_flag" in signals:
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

    if "recruiter_response_rate" in signals and signals.get("recruiter_response_rate") is not None:
        response_rate = _rate(signals.get("recruiter_response_rate"))
        if response_rate >= 0.7:
            score += 2.0
        elif response_rate >= 0.5:
            score += 1.2
        elif response_rate >= 0.3:
            score += 0.5
        elif response_rate < 0.15:
            flags.append("low recruiter response")

    if "avg_response_time_hours" in signals and signals.get("avg_response_time_hours") is not None:
        response_hours = _as_float(signals.get("avg_response_time_hours"))
        if 0 <= response_hours <= 24:
            score += 1.2
        elif response_hours <= 72:
            score += 0.8
        elif response_hours <= 168:
            score += 0.3

    if "notice_period_days" in signals and signals.get("notice_period_days") is not None:
        notice = max(int(signals.get("notice_period_days") or 0), 0)
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
    country = str(profile.get("country", "")).strip()
    is_india = country.casefold() in {"india", "in", "ind"} or (
        not country and bool(TARGET_CITY_PATTERN.search(location))
    )

    if is_india:
        score += 2.0
    elif country:
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


def _skill_trust_score(skills: Iterable[Mapping], signals: Mapping, career_evidence: int) -> float:
    assessment_scores = signals.get("skill_assessment_scores", {})
    total = 0.0
    relevant_count = 0
    buzzword_count = 0
    for skill in skills:
        raw_name = str(skill.get("name", ""))
        name = _canonical_skill(raw_name)
        if name is None:
            continue
        relevant_count += 1
        score = 1.0
        duration = int(skill.get("duration_months") or 0)
        proficiency = str(skill.get("proficiency", ""))
        endorsements = int(skill.get("endorsements") or 0)

        if duration >= 24:
            score += 0.8
        elif duration >= 12:
            score += 0.5
        elif duration <= 6:
            score -= 0.5

        if proficiency == "expert":
            score += 0.7
        elif proficiency == "advanced":
            score += 0.45
        elif proficiency == "beginner":
            score -= 0.25

        if endorsements >= 20:
            score += 0.3
        elif endorsements >= 10:
            score += 0.15

        assessment = 0.0
        if isinstance(assessment_scores, Mapping):
            assessment = _assessment_score(assessment_scores, raw_name, name)
        if assessment >= 85:
            score += 0.8
        elif assessment >= 70:
            score += 0.5

        if career_evidence >= 8:
            score += 0.7
        elif career_evidence >= 4:
            score += 0.35

        if name in {"LLMs", "RAG", "Pinecone", "Qdrant", "Weaviate", "Vector Search", "Fine-tuning LLMs"}:
            buzzword_count += 1
            if career_evidence < 4:
                score -= 1.0

        total += max(score, 0.0)

    if buzzword_count >= 4 and career_evidence < 4:
        total *= 0.55
    if relevant_count >= 8 and career_evidence < 4:
        total *= 0.7
    return total


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
    service_companies = {company.casefold() for company in SERVICE_COMPANIES}
    if str(profile.get("current_company", "")).casefold() in service_companies:
        penalty += 4.0
    if str(profile.get("current_industry", "")).casefold() in {"it services", "consulting"}:
        penalty += 3.0
    if _experience_history_gap(profile, history) > 5.0:
        penalty += 8.0
    if "outside India" in risk_flags:
        penalty += 14.0 if bool(signals.get("willing_to_relocate")) else 25.0
    if "not marked open to work" in risk_flags:
        penalty += 6.0
    if "non-target ML domain" in risk_flags:
        penalty += 12.0
    if "generic AI without shipped retrieval evidence" in risk_flags:
        penalty += 18.0
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


def _generic_ai_flags(
    profile: Mapping,
    history: Iterable[Mapping],
    skills: Iterable[Mapping],
    target_evidence: int,
) -> list[str]:
    text = " ".join(
        [
            str(profile.get("headline", "")),
            str(profile.get("summary", "")),
            _career_text(history),
            " ".join(str(skill.get("name", "")) for skill in skills),
        ]
    ).lower()
    generic_terms = ("langchain", "openai", "prompt engineering", "rag template", "tutorial")
    demo_terms = ("demo", "demos", "proof-of-concept", "proof of concept", "poc", "template", "tutorial")
    shipped_terms = ("shipped", "production", "owned", "deployed", "serving", "a/b", "ndcg", "mrr")
    if (
        any(term in text for term in generic_terms)
        and any(term in text for term in demo_terms)
        and target_evidence <= 4
        and not any(term in text for term in shipped_terms)
    ):
        return ["generic AI without shipped retrieval evidence"]
    if (
        any(term in text for term in generic_terms)
        and "no production retrieval" in text
        and target_evidence <= 5
    ):
        return ["generic AI without shipped retrieval evidence"]
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


def _rate(value: object) -> float:
    rate = _as_float(value)
    if 1.0 < rate <= 100.0:
        return rate / 100.0
    return rate


def _assessment_score(scores: Mapping, raw_name: str, canonical_name: str) -> float:
    if raw_name in scores:
        return _as_float(scores[raw_name])
    if canonical_name in scores:
        return _as_float(scores[canonical_name])
    normalized = {
        re.sub(r"[^a-z0-9]+", " ", str(key).casefold()).strip(): value
        for key, value in scores.items()
    }
    for name in (raw_name, canonical_name):
        key = re.sub(r"[^a-z0-9]+", " ", name.casefold()).strip()
        if key in normalized:
            return _as_float(normalized[key])
    return 0.0


def _as_float(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(number) or math.isinf(number):
        return 0.0
    return number
