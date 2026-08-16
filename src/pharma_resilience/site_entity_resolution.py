from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
from typing import Any

from .audit_summary import read_csv


TRUE_VALUES = {
    "1",
    "true",
    "yes",
}


UNKNOWN_VALUES = {
    "",
    "unknown",
    "indeterminate",
    "none",
    "na",
    "n/a",
}


TURKISH_MAP = str.maketrans(
    {
        "ı": "i",
        "İ": "I",
        "ş": "s",
        "Ş": "S",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
    }
)


def _ascii_fold(text: str) -> str:
    text = text.translate(TURKISH_MAP)

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def normalize_site_text(
    value: str | None,
) -> str:
    value = (value or "").strip()

    if value.casefold() in UNKNOWN_VALUES:
        return ""

    value = _ascii_fold(value).casefold()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return " ".join(
        value.split()
    )


def company_prefix_key(
    value: str | None,
) -> str:
    value = (value or "").strip()

    if not value:
        return ""

    prefix = re.split(
        r"[,;]",
        value,
        maxsplit=1,
    )[0]

    return normalize_site_text(prefix)


def _token_set(
    normalized: str,
) -> set[str]:
    return {
        token
        for token in normalized.split()
        if token
    }


def token_jaccard(
    left: str,
    right: str,
) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)

    if not left_tokens and not right_tokens:
        return 1.0

    if not left_tokens or not right_tokens:
        return 0.0

    intersection = len(
        left_tokens & right_tokens
    )

    union = len(
        left_tokens | right_tokens
    )

    return intersection / union


def lexical_similarity(
    left: str,
    right: str,
) -> float:
    if not left and not right:
        return 1.0

    if not left or not right:
        return 0.0

    return SequenceMatcher(
        None,
        left,
        right,
    ).ratio()


def extract_site_mentions(
    evidence_csv: str | Path,
) -> dict[str, dict[str, Any]]:
    rows = read_csv(evidence_csv)

    mentions: dict[
        str,
        dict[str, Any],
    ] = {}

    for row in rows:
        field_name = (
            row.get("field_name") or ""
        ).strip()

        if field_name != "manufacturing_site":
            continue

        field_present = (
            row.get("field_present") or ""
        ).strip().casefold()

        if field_present not in TRUE_VALUES:
            continue

        raw_value = (
            row.get("observed_value") or ""
        ).strip()

        normalized = normalize_site_text(
            raw_value
        )

        if not normalized:
            continue

        product_id = (
            row.get("product_id") or ""
        ).strip()

        if raw_value not in mentions:
            mentions[raw_value] = {
                "raw_mention": raw_value,
                "normalized_text": normalized,
                "company_prefix_key": (
                    company_prefix_key(
                        raw_value
                    )
                ),
                "product_ids": set(),
                "observation_count": 0,
            }

        mentions[
            raw_value
        ]["observation_count"] += 1

        if product_id:
            mentions[
                raw_value
            ]["product_ids"].add(
                product_id
            )

    return {
        raw: {
            **values,
            "product_ids": sorted(
                values["product_ids"]
            ),
        }
        for raw, values in sorted(
            mentions.items()
        )
    }


def compare_site_mentions(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any] | None:
    left_norm = left[
        "normalized_text"
    ]

    right_norm = right[
        "normalized_text"
    ]

    left_prefix = left[
        "company_prefix_key"
    ]

    right_prefix = right[
        "company_prefix_key"
    ]

    jaccard = token_jaccard(
        left_norm,
        right_norm,
    )

    sequence = lexical_similarity(
        left_norm,
        right_norm,
    )

    reason = None
    candidate_score = 0.0

    if left_norm == right_norm:
        reason = "exact_lexical_match"
        candidate_score = 1.0

    elif (
        left_prefix
        and right_prefix
        and left_prefix == right_prefix
    ):
        reason = "same_company_prefix"
        candidate_score = 0.95

    elif (
        left_norm in right_norm
        or right_norm in left_norm
    ):
        reason = "normalized_containment"
        candidate_score = max(
            0.80,
            sequence,
        )

    elif max(
        jaccard,
        sequence,
    ) >= 0.72:
        reason = "lexical_similarity"
        candidate_score = max(
            jaccard,
            sequence,
        )

    if reason is None:
        return None

    return {
        "left_raw_mention": (
            left["raw_mention"]
        ),
        "right_raw_mention": (
            right["raw_mention"]
        ),
        "left_product_ids": (
            left["product_ids"]
        ),
        "right_product_ids": (
            right["product_ids"]
        ),
        "left_normalized_text": (
            left_norm
        ),
        "right_normalized_text": (
            right_norm
        ),
        "left_company_prefix_key": (
            left_prefix
        ),
        "right_company_prefix_key": (
            right_prefix
        ),
        "token_jaccard": round(
            jaccard,
            4,
        ),
        "sequence_similarity": round(
            sequence,
            4,
        ),
        "candidate_score": round(
            candidate_score,
            4,
        ),
        "candidate_reason": reason,
        "decision": "review_required",
        "resolved_entity_id": "",
        "review_notes": (
            "Candidate only. Do not merge site mentions "
            "without manual evidence that they refer to "
            "the same physical facility."
        ),
    }


def generate_site_candidates(
    evidence_csv: str | Path,
) -> dict[str, Any]:
    mentions = extract_site_mentions(
        evidence_csv
    )

    candidates: list[
        dict[str, Any]
    ] = []

    mention_values = list(
        mentions.values()
    )

    for left, right in combinations(
        mention_values,
        2,
    ):
        candidate = compare_site_mentions(
            left,
            right,
        )

        if candidate is not None:
            candidates.append(
                candidate
            )

    candidates.sort(
        key=lambda row: (
            -row["candidate_score"],
            row["left_raw_mention"],
            row["right_raw_mention"],
        )
    )

    return {
        "n_unique_raw_mentions": len(
            mentions
        ),
        "n_candidate_pairs": len(
            candidates
        ),
        "n_resolved_entities": 0,
        "auto_merge_performed": False,
        "site_mentions": mentions,
        "candidate_pairs": candidates,
        "interpretation": (
            "Candidate generation is lexical only. "
            "No candidate pair is automatically treated "
            "as the same physical facility."
        ),
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Site Entity Resolution Candidates v0.1"
    )
    lines.append("")

    lines.append(
        "Candidate generation for manual resolution "
        "of manufacturing-site mentions."
    )
    lines.append("")

    lines.append(
        "> Lexical similarity is not evidence of physical "
        "facility identity."
    )
    lines.append("")

    lines.append(
        f"- Unique raw site mentions: "
        f"**{summary['n_unique_raw_mentions']}**"
    )

    lines.append(
        f"- Candidate pairs requiring review: "
        f"**{summary['n_candidate_pairs']}**"
    )

    lines.append(
        f"- Automatically merged entities: **0**"
    )

    lines.append("")
    lines.append("## Candidate pairs")
    lines.append("")

    candidates = summary[
        "candidate_pairs"
    ]

    if not candidates:
        lines.append(
            "No lexical candidate pairs were generated."
        )

        return "\n".join(lines)

    lines.append(
        "| Score | Reason | Left mention | "
        "Right mention | Decision |"
    )

    lines.append(
        "|---:|---|---|---|---|"
    )

    for candidate in candidates:
        left = candidate[
            "left_raw_mention"
        ].replace(
            "|",
            "/",
        )

        right = candidate[
            "right_raw_mention"
        ].replace(
            "|",
            "/",
        )

        lines.append(
            f"| {candidate['candidate_score']:.2f} | "
            f"`{candidate['candidate_reason']}` | "
            f"{left} | "
            f"{right} | "
            f"`{candidate['decision']}` |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")

    lines.append(
        "Pairs in this table are candidates for manual "
        "entity review only. A shared company name, address "
        "fragment, or high lexical similarity does not prove "
        "that two records identify the same manufacturing "
        "facility."
    )

    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate conservative candidate pairs "
            "for manufacturing-site entity resolution."
        )
    )

    parser.add_argument(
        "evidence_csv"
    )

    parser.add_argument(
        "--json-out"
    )

    parser.add_argument(
        "--md-out"
    )

    args = parser.parse_args()

    summary = generate_site_candidates(
        args.evidence_csv
    )

    markdown = render_markdown(
        summary
    )

    print(markdown)

    if args.json_out:
        output = Path(
            args.json_out
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    if args.md_out:
        output = Path(
            args.md_out
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            markdown + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()