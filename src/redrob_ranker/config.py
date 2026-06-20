from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringWeights:
    """Transparent calibration for the Senior AI Engineer ranking objective."""

    role: float = 4.5
    seniority: float = 2.0
    retrieval: float = 3.0
    ranking: float = 3.4
    evaluation: float = 2.2
    profile_evidence: float = 1.0
    skills: float = 0.8
    product_experience: float = 1.15
    production: float = 2.4
    engineering: float = 1.6
    leadership: float = 1.2
    confidence: float = 1.5
    availability: float = 1.4
    logistics: float = 1.4
    severe_evidence_gap: float = 12.0
    moderate_evidence_gap: float = 5.0


DEFAULT_WEIGHTS = ScoringWeights()
