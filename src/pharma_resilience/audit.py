from collections import Counter


VALID_RESOLUTION = {"explicit", "partial", "ambiguous", "absent"}
VALID_RELATION = {"required", "alternative", "unknown"}
VALID_EXHAUSTIVENESS = {
    "explicit_complete",
    "explicitly_partial",
    "single_record_only",
    "unknown",
}


def missingness_rate(values, unknown_tokens=("unknown", "absent", "", None)):
    vals = list(values)
    if not vals:
        return None
    return sum(v in unknown_tokens for v in vals) / len(vals)


def observability_summary(rows: list[dict], field: str) -> dict:
    values = [r.get(field) for r in rows]
    c = Counter(values)
    n = len(values)
    return {
        "field": field,
        "n": n,
        "counts": dict(c),
        "unknown_rate": missingness_rate(values),
    }


def validate_evidence_row(row: dict) -> list[str]:
    issues = []
    if row.get("resolution") not in VALID_RESOLUTION:
        issues.append("invalid resolution")
    return issues
