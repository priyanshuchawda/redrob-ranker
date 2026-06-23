from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field


@dataclass
class RoleRequirementMatrix:
    role_title: str
    must_have_skills: list[str] = field(default_factory=list)
    strong_signal_skills: list[str] = field(default_factory=list)
    good_to_have_skills: list[str] = field(default_factory=list)
    seniority_expectations: str = ""
    domain_expectations: str = ""
    production_expectations: str = ""
    leadership_expectations: str = ""
    location_requirements: str = ""
    availability_requirements: str = ""
    risk_blockers: list[str] = field(default_factory=list)
    raw_job_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def default_role_requirements() -> RoleRequirementMatrix:
    raw = (
        "Senior AI Engineer for a founding AI team. Must have Python, machine learning, "
        "retrieval, ranking, recommendation, evaluation, and production engineering. "
        "Strong signals include shipped semantic search, vector search, candidate matching, "
        "learning to rank, reranking, NDCG/MRR evaluation, and product-company ownership. "
        "Expected seniority is 5-9 years, India-friendly logistics, active availability, "
        "and practical leadership without pure research-only or demo-only experience."
    )
    return RoleRequirementMatrix(
        role_title="Senior AI Engineer",
        must_have_skills=["Python", "Machine Learning", "retrieval", "ranking", "evaluation"],
        strong_signal_skills=[
            "semantic search",
            "vector search",
            "candidate matching",
            "learning to rank",
            "reranking",
            "production retrieval",
        ],
        good_to_have_skills=["FastAPI", "Docker", "Kubernetes", "MLOps", "recommendation systems"],
        seniority_expectations="5-9 years experience",
        domain_expectations="AI/ML product systems, search, retrieval, ranking, matching, recommendations",
        production_expectations="shipped production systems with measurable quality, latency, or product impact",
        leadership_expectations="ownership, mentoring, architecture, founding-team execution",
        location_requirements="India, preferably Pune, Noida, Delhi NCR, Mumbai, Hyderabad, or Bangalore",
        availability_requirements="active, responsive, open to work, reasonable notice period",
        risk_blockers=[
            "no production ownership",
            "keyword stuffing",
            "generic AI demos",
            "non-target ML domain without retrieval depth",
        ],
        raw_job_text=raw,
    )


def parse_job_description(job_text: str) -> RoleRequirementMatrix:
    text = job_text.strip()
    if not text:
        return default_role_requirements()

    lines = [line.strip(" \t-*") for line in text.splitlines() if line.strip()]
    role_title = _infer_role_title(lines, text)
    lower = text.lower()

    return RoleRequirementMatrix(
        role_title=role_title,
        must_have_skills=_extract_list_after_label(text, ("must have", "required skills", "requirements")),
        strong_signal_skills=_extract_list_after_label(text, ("strong signals", "strong signal", "preferred proof")),
        good_to_have_skills=_extract_list_after_label(text, ("good to have", "nice to have", "bonus")),
        seniority_expectations=_extract_seniority(text),
        domain_expectations=_extract_sentence_with(lower, text, ("domain", "search", "retrieval", "ranking", "matching")),
        production_expectations=_extract_sentence_with(lower, text, ("production", "shipped", "deployed", "serving")),
        leadership_expectations=_extract_sentence_with(lower, text, ("leadership", "mentor", "architecture", "own")),
        location_requirements=_extract_location(text),
        availability_requirements=_extract_availability(text),
        risk_blockers=_extract_list_after_label(text, ("risk blockers", "blockers", "red flags")),
        raw_job_text=text,
    )


def _infer_role_title(lines: list[str], text: str) -> str:
    first = lines[0] if lines else ""
    if 2 <= len(first.split()) <= 8 and not first.lower().startswith(("must", "strong", "good")):
        return first.rstrip(":")
    match = re.search(r"\b((?:senior|lead|staff|principal|founding)?\s*[A-Z][A-Za-z /+-]*(?:Engineer|Scientist|Manager))\b", text)
    if match:
        return " ".join(match.group(1).split())
    return "Unclear role"


def _extract_list_after_label(text: str, labels: tuple[str, ...]) -> list[str]:
    for label in labels:
        pattern = re.compile(rf"{re.escape(label)}\s*:\s*(.+?)(?:\n|$)", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            return _split_items(match.group(1))
    return []


def _split_items(value: str) -> list[str]:
    value = re.sub(r"\band\b", ",", value, flags=re.IGNORECASE)
    parts = [part.strip(" .;") for part in re.split(r"[,|;/]", value)]
    return [part for part in parts if part]


def _extract_seniority(text: str) -> str:
    match = re.search(r"(\d+\s*[-+]\s*\d*\s*years?(?:\s+experience)?)", text, re.IGNORECASE)
    if match:
        value = re.sub(r"\s+", " ", match.group(1)).replace(" - ", "-")
        return value if "experience" in value.lower() else f"{value} experience"
    match = re.search(r"(\d+\s+to\s+\d+\s+years?(?:\s+experience)?)", text, re.IGNORECASE)
    if match:
        return re.sub(r"\s+", " ", match.group(1))
    return ""


def _extract_sentence_with(lower: str, original: str, terms: tuple[str, ...]) -> str:
    sentences = re.split(r"(?<=[.!?])\s+|\n", original)
    for sentence in sentences:
        if any(term in sentence.lower() for term in terms):
            return sentence.strip(" .")
    return ""


def _extract_location(text: str) -> str:
    match = re.search(r"location\s*:\s*(.+?)(?:\.|\n|$)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    cities = re.findall(r"\b(Pune|Bangalore|Bengaluru|Delhi|Noida|Gurgaon|Gurugram|Mumbai|Hyderabad|India)\b", text)
    return ", ".join(dict.fromkeys(cities))


def _extract_availability(text: str) -> str:
    match = re.search(r"(notice\s+(?:under|within|period)?\s*\d+\s*days?)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    sentence = _extract_sentence_with(text.lower(), text, ("availability", "notice", "open to work"))
    return sentence
