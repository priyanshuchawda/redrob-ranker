from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from redrob_ranker.ai_fusion import (
    DEFAULT_GEMINI_MODEL,
    ai_metadata,
    build_signal_fusion_summary,
    clamp_score,
    detect_hidden_gem,
    fallback_ai_jd_insight,
    fallback_contextual_fit,
    fallback_recruiter_explanation,
)


PROTECTED_ATTRIBUTE_GUARDRAILS = (
    "Do not infer or use gender, age, caste, religion, race, disability, marital status, "
    "family status, ethnicity, nationality beyond job logistics, or any protected trait. "
    "Use only supplied candidate data, score breakdown, evidence ledger, risk radar and job matrix. "
    "Do not invent achievements. If evidence is missing, write \"Missing from supplied data\". "
    "Return valid JSON only."
)


def _load_local_env() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class GeminiService:
    def __init__(self) -> None:
        _load_local_env()
        self.model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)

    @property
    def enabled(self) -> bool:
        return os.getenv("GEMINI_ENABLED", "false").strip().lower() == "true" and bool(os.getenv("GEMINI_API_KEY"))

    def generate_ai_jd_insight(self, job_text: str | None, deterministic_matrix: dict[str, Any] | None) -> dict[str, Any]:
        fallback = fallback_ai_jd_insight(deterministic_matrix or {}, model=self.model)
        prompt = {
            "task": "Gemini assisted insight for job description understanding.",
            "guardrails": PROTECTED_ATTRIBUTE_GUARDRAILS,
            "job_text": job_text or "",
            "deterministic_matrix": deterministic_matrix or {},
            "schema": {
                "role_archetype": "",
                "must_have_skills": [],
                "semantic_skill_synonyms": [],
                "strong_success_signals": [],
                "seniority_expectations": [],
                "domain_expectations": [],
                "negative_signals": [],
                "hiring_constraints": [],
                "interview_focus_areas": [],
                "confidence": 0.0,
                "missing_information": [],
            },
        }
        return self._generate_json(prompt, fallback, normalizer=_normalize_jd_insight)

    def generate_contextual_fit(
        self,
        candidate_payload: dict[str, Any],
        job_matrix: dict[str, Any] | None,
        evidence_ledger: dict[str, Any] | None,
        risk_radar: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        fallback = fallback_contextual_fit(candidate_payload, model=self.model)
        prompt = {
            "task": "Gemini assisted contextual relevance. Do not alter deterministic final score.",
            "guardrails": PROTECTED_ATTRIBUTE_GUARDRAILS,
            "candidate_payload": candidate_payload,
            "job_matrix": job_matrix or {},
            "evidence_ledger": evidence_ledger or {},
            "risk_radar": risk_radar or [],
            "schema": {
                "contextual_fit_score": 0,
                "semantic_fit_reason": "",
                "hidden_strengths": [],
                "weak_context_signals": [],
                "evidence_supported": [],
                "evidence_missing": [],
                "risk_notes": [],
                "recommended_interview_checks": [],
            },
        }
        return self._generate_json(prompt, fallback, normalizer=_normalize_contextual_fit)

    def generate_recruiter_explanation(
        self,
        candidate_payload: dict[str, Any],
        score_breakdown: dict[str, Any],
        evidence_ledger: dict[str, Any] | None,
        risk_radar: list[dict[str, Any]] | None,
        ai_contextual_fit: dict[str, Any] | None,
    ) -> dict[str, Any]:
        fallback = fallback_recruiter_explanation(candidate_payload, model=self.model)
        prompt = {
            "task": "Gemini assisted recruiter explanation.",
            "guardrails": PROTECTED_ATTRIBUTE_GUARDRAILS,
            "candidate_payload": candidate_payload,
            "score_breakdown": score_breakdown,
            "evidence_ledger": evidence_ledger or {},
            "risk_radar": risk_radar or [],
            "ai_contextual_fit": ai_contextual_fit or {},
            "schema": {
                "executive_summary": "",
                "why_shortlisted": [],
                "strongest_evidence": [],
                "hidden_strengths": [],
                "concerns": [],
                "missing_proof": [],
                "interview_questions": [],
                "final_recruiter_note": "",
            },
        }
        return self._generate_json(prompt, fallback, normalizer=_normalize_recruiter_explanation)

    def enrich_payload(self, payload: dict[str, Any], job_text: str | None = None) -> dict[str, Any]:
        payload["ai_jd_insight"] = self.generate_ai_jd_insight(job_text, payload.get("role_requirements") or {})
        rows = payload.get("rankings") or []
        for row in rows:
            contextual_fit = self.generate_contextual_fit(
                row,
                payload.get("role_requirements") or {},
                row.get("evidence_ledger") or {},
                row.get("risks") or [],
            )
            row["ai_contextual_fit"] = contextual_fit
            row["ai_recruiter_explanation"] = self.generate_recruiter_explanation(
                row,
                row.get("components") or {},
                row.get("evidence_ledger") or {},
                row.get("risks") or [],
                contextual_fit,
            )
            row.update(detect_hidden_gem(row, rows, contextual_fit))
            row["signal_fusion_summary"] = build_signal_fusion_summary(row, contextual_fit)
        return payload

    def hidden_gems(self, payload: dict[str, Any]) -> dict[str, Any]:
        rows = payload.get("rankings") or []
        gems = [row for row in rows if row.get("hidden_gem_candidate")]
        return {
            **ai_metadata(enabled=self.enabled, model=self.model, fallback_used=not self.enabled),
            "hidden_gems": [
                {
                    "candidate_id": row.get("candidate_id"),
                    "hidden_gem_reason": row.get("hidden_gem_reason"),
                    "hidden_gem_evidence": row.get("hidden_gem_evidence") or [],
                }
                for row in gems
            ],
        }

    def signal_fusion_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            **ai_metadata(enabled=self.enabled, model=self.model, fallback_used=not self.enabled),
            "summary": [
                {
                    "candidate_id": row.get("candidate_id"),
                    "signal_fusion_summary": row.get("signal_fusion_summary") or build_signal_fusion_summary(row, row.get("ai_contextual_fit")),
                }
                for row in payload.get("rankings", [])
            ],
        }

    def trust_audit_ai_summary(self, audit: dict[str, Any]) -> dict[str, Any]:
        return {
            **ai_metadata(enabled=self.enabled, model=self.model, fallback_used=True),
            "summary": "Gemini assisted insight is optional. Verify missing evidence, weak proof, high-risk profiles and low-confidence candidates before outreach.",
            "verification_priorities": [
                "Validate missing career-backed proof.",
                "Review weak contextual signals.",
                "Check high-risk and location or availability concerns.",
            ],
            "audit_snapshot": {
                "total_candidates": audit.get("total_candidates"),
                "high_risk_candidate_count": audit.get("high_risk_candidate_count"),
                "candidates_with_missing_evidence": audit.get("candidates_with_missing_evidence"),
                "low_confidence_count": audit.get("low_confidence_count"),
            },
        }

    def _generate_json(self, prompt: dict[str, Any], fallback: dict[str, Any], *, normalizer) -> dict[str, Any]:
        if not self.enabled:
            return fallback
        try:
            raw_text = self._call_gemini(prompt)
            parsed = _parse_json(raw_text)
            normalized = normalizer(parsed)
            return {
                **fallback,
                **normalized,
                **ai_metadata(enabled=True, model=self.model, fallback_used=False),
            }
        except Exception:
            return fallback

    def _call_gemini(self, prompt: dict[str, Any]) -> str:
        from google import genai  # type: ignore

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=self.model,
            contents=json.dumps(prompt, ensure_ascii=False),
            config={"response_mime_type": "application/json"},
        )
        return getattr(response, "text", "") or ""


def _parse_json(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response must be a JSON object")
    return parsed


def _normalize_jd_insight(parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "role_archetype": str(parsed.get("role_archetype") or ""),
        "must_have_skills": _strings(parsed.get("must_have_skills")),
        "semantic_skill_synonyms": _strings(parsed.get("semantic_skill_synonyms")),
        "strong_success_signals": _strings(parsed.get("strong_success_signals")),
        "seniority_expectations": _strings(parsed.get("seniority_expectations")),
        "domain_expectations": _strings(parsed.get("domain_expectations")),
        "negative_signals": _strings(parsed.get("negative_signals")),
        "hiring_constraints": _strings(parsed.get("hiring_constraints")),
        "interview_focus_areas": _strings(parsed.get("interview_focus_areas")),
        "confidence": max(0.0, min(1.0, float(parsed.get("confidence") or 0.0))),
        "missing_information": _strings(parsed.get("missing_information")),
    }


def _normalize_contextual_fit(parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "contextual_fit_score": clamp_score(parsed.get("contextual_fit_score")),
        "semantic_fit_reason": str(parsed.get("semantic_fit_reason") or "Missing from supplied data"),
        "hidden_strengths": _strings(parsed.get("hidden_strengths")),
        "weak_context_signals": _strings(parsed.get("weak_context_signals")),
        "evidence_supported": _strings(parsed.get("evidence_supported")),
        "evidence_missing": _strings(parsed.get("evidence_missing")),
        "risk_notes": _strings(parsed.get("risk_notes")),
        "recommended_interview_checks": _strings(parsed.get("recommended_interview_checks")),
    }


def _normalize_recruiter_explanation(parsed: dict[str, Any]) -> dict[str, Any]:
    return {
        "executive_summary": str(parsed.get("executive_summary") or "Missing from supplied data"),
        "why_shortlisted": _strings(parsed.get("why_shortlisted")) or ["Missing from supplied data"],
        "strongest_evidence": _strings(parsed.get("strongest_evidence")) or ["Missing from supplied data"],
        "hidden_strengths": _strings(parsed.get("hidden_strengths")),
        "concerns": _strings(parsed.get("concerns")) or ["Missing from supplied data"],
        "missing_proof": _strings(parsed.get("missing_proof")) or ["Missing from supplied data"],
        "interview_questions": _strings(parsed.get("interview_questions")) or ["Missing from supplied data"],
        "final_recruiter_note": str(parsed.get("final_recruiter_note") or "Missing from supplied data"),
    }


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item).strip()]
    return [str(value)]


gemini_service = GeminiService()
