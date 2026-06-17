from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CandidateFeatures:
    candidate_id: str
    current_title: str
    years_of_experience: float
    location: str
    country: str
    role_score: float
    seniority_score: float
    retrieval_evidence: int
    ranking_evidence: int
    evaluation_evidence: int
    product_company_months: int
    relevant_skill_count: int
    relevant_skills: tuple[str, ...]
    evidence_phrases: tuple[str, ...]
    availability_score: float
    logistics_score: float
    risk_penalty: float
    keyword_stuffing_risk: bool
    risk_flags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ScoreComponents:
    role: float
    seniority: float
    retrieval: float
    ranking: float
    evaluation: float
    skills: float
    product: float
    availability: float
    logistics: float
    risk: float
    total: float


@dataclass(frozen=True)
class ScoredCandidate:
    candidate_id: str
    score: float
    candidate: dict
    features: CandidateFeatures
    components: ScoreComponents


@dataclass(frozen=True)
class RankedCandidate:
    candidate_id: str
    rank: int
    score: float
    reasoning: str
