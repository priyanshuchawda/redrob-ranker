from __future__ import annotations

from copy import deepcopy
from typing import Any


PROTECTED_ATTRIBUTE_KEYS = {
    "age",
    "caste",
    "disability",
    "disabled",
    "gender",
    "marital_status",
    "married",
    "political_views",
    "race",
    "religion",
    "sexual_orientation",
}


def uses_role_relevant_evidence_only() -> bool:
    return True


def strip_protected_attributes(candidate: dict) -> tuple[dict, list[str]]:
    cleaned = deepcopy(candidate)
    ignored: list[str] = []

    def scrub(value: Any, path: str = "") -> Any:
        if isinstance(value, dict):
            result: dict = {}
            for key, item in value.items():
                normalized = str(key).casefold().replace(" ", "_").replace("-", "_")
                if normalized in PROTECTED_ATTRIBUTE_KEYS:
                    ignored.append(normalized)
                    continue
                result[key] = scrub(item, f"{path}.{key}" if path else str(key))
            return result
        if isinstance(value, list):
            return [scrub(item, path) for item in value]
        return value

    return scrub(cleaned), list(dict.fromkeys(ignored))


def fairness_metadata() -> dict:
    return {
        "ranking_uses_role_relevant_evidence_only": True,
        "ignored_attributes": sorted(PROTECTED_ATTRIBUTE_KEYS),
    }

