from __future__ import annotations

import csv
import gzip
import json
import re
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


@dataclass
class CandidateRecord:
    candidate_id: str
    name: str = ""
    raw_text: str = ""
    skills: list[str] = field(default_factory=list)
    work_history: list[dict] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    location: str = ""
    availability: str = ""
    metadata: dict = field(default_factory=dict)
    raw_record: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_scoring_dict(self) -> dict:
        raw = deepcopy(self.raw_record)
        if _looks_like_challenge_candidate(raw):
            raw.setdefault("candidate_id", self.candidate_id)
            return raw

        skills = [
            skill if isinstance(skill, dict) else {"name": str(skill), "proficiency": "", "duration_months": 0}
            for skill in self.skills
        ]
        history = self.work_history or [
            {
                "company": "",
                "title": _first(raw, ("title", "current_title", "role")),
                "duration_months": 0,
                "is_current": True,
                "industry": _first(raw, ("industry", "domain")),
                "description": self.raw_text,
            }
        ]
        profile = {
            "anonymized_name": self.name,
            "headline": _first(raw, ("headline", "title", "current_title", "role")),
            "summary": self.raw_text,
            "location": self.location,
            "country": _infer_country(self.location),
            "years_of_experience": _first(raw, ("years_of_experience", "experience_years", "years"), 0.0),
            "current_title": _first(raw, ("title", "current_title", "role")),
            "current_company": _first(raw, ("company", "current_company")),
            "current_industry": _first(raw, ("industry", "domain")),
        }
        signals = {
            "open_to_work_flag": _parse_open_to_work(self.availability),
            "notice_period_days": _parse_notice_days(self.availability),
            "willing_to_relocate": _parse_bool(_first(raw, ("willing_to_relocate", "relocation"))),
        }
        return {
            "candidate_id": self.candidate_id,
            "profile": profile,
            "career_history": history,
            "projects": self.projects,
            "education": self.education,
            "skills": skills,
            "redrob_signals": {key: value for key, value in signals.items() if value is not None},
            "_source_metadata": self.metadata,
            "_raw_record": raw,
        }


def load_candidate_records(path: str | Path, data_quality_report_path: str | Path | None = None) -> list[CandidateRecord]:
    source = Path(path)
    raw_records, source_format, assumptions = _read_records(source)
    records: list[CandidateRecord] = []
    malformed_rows: list[dict] = []
    seen: set[str] = set()

    for index, raw in enumerate(raw_records, start=1):
        try:
            record = adapt_candidate_record(raw)
        except ValueError as exc:
            malformed_rows.append({"row": index, "error": str(exc)})
            continue
        if record.candidate_id in seen:
            raise ValueError(f"Duplicate candidate_id: {record.candidate_id}")
        seen.add(record.candidate_id)
        records.append(record)

    report = {
        "source": str(source),
        "source_format": source_format,
        "loaded_records": len(records),
        "malformed_rows": malformed_rows,
        "duplicate_ids": [],
        "assumptions": list(dict.fromkeys([*assumptions, *[r.metadata.get("schema_assumption", "") for r in records if r.metadata.get("schema_assumption")]])),
        "field_coverage": _field_coverage(records),
    }
    if data_quality_report_path:
        report_path = Path(data_quality_report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if malformed_rows:
        first = malformed_rows[0]
        raise ValueError(f"Malformed candidate row {first['row']}: {first['error']}")

    return records


def adapt_candidate_record(raw_record: Mapping[str, Any]) -> CandidateRecord:
    if not isinstance(raw_record, Mapping):
        raise ValueError("candidate record must be an object")
    raw = dict(raw_record)
    metadata: dict[str, Any] = {}

    source = raw
    if isinstance(raw.get("candidate"), Mapping):
        source = dict(raw["candidate"])
        metadata["schema_assumption"] = "nested candidate payload"
    elif _looks_like_challenge_candidate(raw):
        metadata["schema_assumption"] = "redrob challenge schema"
    else:
        metadata["schema_assumption"] = "best effort flat mapping"

    candidate_id = str(_first(source, ("candidate_id", "id", "candidateId", "uuid", "email"))).strip()
    if not candidate_id:
        raise ValueError("missing candidate_id")

    name = str(_first(source, ("name", "full_name", "anonymized_name")))
    profile = source.get("profile") if isinstance(source.get("profile"), Mapping) else {}
    if not name and isinstance(profile, Mapping):
        name = str(_first(profile, ("name", "full_name", "anonymized_name")))

    skills = _extract_skills(source)
    work_history = _extract_work_history(source)
    raw_text = _extract_raw_text(source, profile, work_history)
    education = _as_list(source.get("education"))
    projects = _as_list(source.get("projects"))
    location = str(_first(source, ("location", "city", "current_location")) or _first(profile, ("location",)))
    availability = str(_first(source, ("availability", "notice_period", "notice")) or _first(source.get("redrob_signals", {}) if isinstance(source.get("redrob_signals"), Mapping) else {}, ("notice_period_days",)))

    return CandidateRecord(
        candidate_id=candidate_id,
        name=name,
        raw_text=raw_text,
        skills=skills,
        work_history=work_history,
        projects=projects,
        education=education,
        location=location,
        availability=availability,
        metadata=metadata,
        raw_record=deepcopy(raw if source is raw else source),
    )


def _read_records(path: Path) -> tuple[list[dict], str, list[str]]:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if suffixes[-2:] == [".jsonl", ".gz"] or path.name.lower().endswith(".jsonl.gz"):
        return _read_jsonl(path, compressed=True), "jsonl.gz", ["gzip JSONL parsed line by line"]
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return _read_jsonl(path, compressed=False), "jsonl", ["JSONL parsed line by line"]
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload], "json", ["JSON array treated as candidate list"]
        if isinstance(payload, Mapping) and isinstance(payload.get("candidates"), list):
            return [dict(item) for item in payload["candidates"]], "json", ["JSON candidates key treated as candidate list"]
        if isinstance(payload, Mapping):
            return [dict(payload)], "json", ["single JSON object treated as one candidate"]
        raise ValueError(f"Unsupported JSON candidate payload in {path}")
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)], "csv", ["CSV columns mapped by common recruiting field names"]
    raise ValueError(f"Unsupported candidate file type: {path}")


def _read_jsonl(path: Path, *, compressed: bool) -> list[dict]:
    records: list[dict] = []
    opener = gzip.open if compressed else open
    with opener(path, "rt", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_number}: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected a JSON object in {path} at line {line_number}")
            records.append(record)
    return records


def _looks_like_challenge_candidate(raw: Mapping[str, Any]) -> bool:
    return "candidate_id" in raw and isinstance(raw.get("profile"), Mapping) and "career_history" in raw


def _extract_skills(source: Mapping[str, Any]) -> list[str]:
    raw_skills = source.get("skills")
    if raw_skills is None:
        raw_skills = source.get("skill_names")
    if isinstance(raw_skills, str):
        return [part.strip() for part in re.split(r"[,;|]", raw_skills) if part.strip()]
    if isinstance(raw_skills, list):
        result: list[str] = []
        for item in raw_skills:
            if isinstance(item, Mapping):
                name = str(item.get("name", "")).strip()
                if name:
                    result.append(name)
            elif str(item).strip():
                result.append(str(item).strip())
        return result
    return []


def _extract_work_history(source: Mapping[str, Any]) -> list[dict]:
    for key in ("career_history", "work_history", "experience", "employment"):
        value = source.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    return []


def _extract_raw_text(source: Mapping[str, Any], profile: Any, work_history: Iterable[Mapping[str, Any]]) -> str:
    chunks: list[str] = []
    for key in ("raw_text", "resume_text", "summary", "headline", "description"):
        value = source.get(key)
        if isinstance(value, str):
            chunks.append(value)
    resume = source.get("resume")
    if isinstance(resume, Mapping):
        for key in ("text", "raw_text", "summary"):
            if isinstance(resume.get(key), str):
                chunks.append(str(resume[key]))
    if isinstance(profile, Mapping):
        for key in ("headline", "summary", "current_title"):
            if isinstance(profile.get(key), str):
                chunks.append(str(profile[key]))
    for item in work_history:
        for key in ("title", "description"):
            if isinstance(item.get(key), str):
                chunks.append(str(item[key]))
    return " ".join(chunk for chunk in chunks if chunk).strip()


def _as_list(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [dict(item) if isinstance(item, Mapping) else {"value": item} for item in value]
    return []


def _first(source: Any, keys: tuple[str, ...], default: Any = "") -> Any:
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return default


def _infer_country(location: str) -> str:
    if "india" in location.casefold() or any(city in location.casefold() for city in ("pune", "bangalore", "bengaluru", "delhi", "mumbai", "hyderabad", "noida", "gurgaon", "gurugram")):
        return "India"
    return ""


def _parse_notice_days(value: str) -> int | None:
    match = re.search(r"(\d+)\s*days?", str(value), re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _parse_open_to_work(value: str) -> bool | None:
    lower = str(value).casefold()
    if "open" in lower or "immediate" in lower:
        return True
    if "not open" in lower:
        return False
    return None


def _parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    lower = str(value).casefold()
    if lower in {"true", "yes", "y", "1"}:
        return True
    if lower in {"false", "no", "n", "0"}:
        return False
    return None


def _field_coverage(records: list[CandidateRecord]) -> dict[str, int]:
    return {
        "name": sum(bool(record.name) for record in records),
        "raw_text": sum(bool(record.raw_text) for record in records),
        "skills": sum(bool(record.skills) for record in records),
        "work_history": sum(bool(record.work_history) for record in records),
        "education": sum(bool(record.education) for record in records),
        "location": sum(bool(record.location) for record in records),
        "availability": sum(bool(record.availability) for record in records),
    }

