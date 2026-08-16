from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import product
from pathlib import Path
from typing import Any

from .audit_summary import read_csv
from .resolution_sensitivity import LEVELS


UNKNOWN_VALUES = {
    "",
    "unknown",
    "indeterminate",
    "none",
    "na",
    "n/a",
}


def _canonical(value: str | None) -> str:
    value = (value or "").strip()

    if value.casefold() in UNKNOWN_VALUES:
        return "unknown"

    return value


def _known(value: str | None) -> bool:
    return _canonical(value) != "unknown"


def _fraction(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 4)


def _complete_signature(
    row: dict[str, str],
    fields: tuple[str, ...],
) -> tuple[str, ...] | None:
    values = tuple(
        _canonical(row.get(field))
        for field in fields
    )

    if "unknown" in values:
        return None

    return values


def _compatible_with_candidate(
    row: dict[str, str],
    fields: tuple[str, ...],
    candidate: tuple[str, ...],
) -> bool:
    for field, target in zip(fields, candidate):
        value = _canonical(row.get(field))

        if value != "unknown" and value != target:
            return False

    return True


def _candidate_values(
    rows: list[dict[str, str]],
    field: str,
) -> list[str]:
    values = sorted(
        {
            _canonical(row.get(field))
            for row in rows
            if _known(row.get(field))
        }
    )

    if values:
        return values

    return ["__unobserved__"]


def _witness(
    signature: tuple[str, ...] | None,
    rows: list[dict[str, str]],
) -> dict[str, Any] | None:
    if signature is None:
        return None

    ingredients = sorted(
        {
            _canonical(row.get("active_ingredient"))
            for row in rows
        }
    )

    return {
        "signature": list(signature),
        "n_products": len(rows),
        "product_ids": sorted(
            (row.get("product_id") or "").strip()
            for row in rows
        ),
        "n_active_ingredients": len(ingredients),
        "active_ingredients": ingredients,
    }


def analyze_bounds_for_level(
    rows: list[dict[str, str]],
    fields: tuple[str, ...],
) -> dict[str, Any]:
    exact_groups: dict[
        tuple[str, ...],
        list[dict[str, str]],
    ] = defaultdict(list)

    complete_rows: list[dict[str, str]] = []

    for row in rows:
        signature = _complete_signature(
            row,
            fields,
        )

        if signature is None:
            continue

        complete_rows.append(row)
        exact_groups[signature].append(row)

    lower_group_size = 0
    lower_span = 0

    lower_group_signature: tuple[str, ...] | None = None
    lower_group_rows: list[dict[str, str]] = []

    lower_span_signature: tuple[str, ...] | None = None
    lower_span_rows: list[dict[str, str]] = []

    for signature, group_rows in exact_groups.items():
        group_size = len(group_rows)

        ingredients = {
            _canonical(row.get("active_ingredient"))
            for row in group_rows
        }

        span = len(ingredients)

        if group_size > lower_group_size:
            lower_group_size = group_size
            lower_group_signature = signature
            lower_group_rows = group_rows

        if span > lower_span:
            lower_span = span
            lower_span_signature = signature
            lower_span_rows = group_rows

    value_lists = [
        _candidate_values(rows, field)
        for field in fields
    ]

    upper_group_size = 0
    upper_span = 0

    upper_group_signature: tuple[str, ...] | None = None
    upper_group_rows: list[dict[str, str]] = []

    upper_span_signature: tuple[str, ...] | None = None
    upper_span_rows: list[dict[str, str]] = []

    n_candidates = 0

    for candidate in product(*value_lists):
        n_candidates += 1

        compatible_rows = [
            row
            for row in rows
            if _compatible_with_candidate(
                row,
                fields,
                candidate,
            )
        ]

        if not compatible_rows:
            continue

        group_size = len(compatible_rows)

        ingredients = {
            _canonical(row.get("active_ingredient"))
            for row in compatible_rows
        }

        span = len(ingredients)

        if group_size > upper_group_size:
            upper_group_size = group_size
            upper_group_signature = candidate
            upper_group_rows = compatible_rows

        if span > upper_span:
            upper_span = span
            upper_span_signature = candidate
            upper_span_rows = compatible_rows

    n_products = len(rows)
    n_complete = len(complete_rows)

    return {
        "fields": list(fields),
        "n_products": n_products,
        "n_complete": n_complete,
        "n_partial": n_products - n_complete,
        "complete_fraction": _fraction(
            n_complete,
            n_products,
        ),
        "n_candidate_completions_evaluated": n_candidates,

        "largest_group_bounds": {
            "lower": lower_group_size,
            "upper": upper_group_size,
            "width": upper_group_size - lower_group_size,
            "lower_witness": _witness(
                lower_group_signature,
                lower_group_rows,
            ),
            "upper_witness": _witness(
                upper_group_signature,
                upper_group_rows,
            ),
        },

        "max_active_ingredient_span_bounds": {
            "lower": lower_span,
            "upper": upper_span,
            "width": upper_span - lower_span,
            "lower_witness": _witness(
                lower_span_signature,
                lower_span_rows,
            ),
            "upper_witness": _witness(
                upper_span_signature,
                upper_span_rows,
            ),
        },

        "certain_cross_ingredient_convergence": (
            lower_span >= 2
        ),

        "possible_cross_ingredient_convergence": (
            upper_span >= 2
        ),
    }


def analyze_partial_observability(
    product_csv: str | Path,
) -> dict[str, Any]:
    rows = read_csv(product_csv)

    levels = {
        level_name: analyze_bounds_for_level(
            rows,
            fields,
        )
        for level_name, fields in LEVELS.items()
    }

    return {
        "n_products": len(rows),
        "interpretation": (
            "Bounds apply to convergence at the modeled "
            "resolution. Unknown fields are treated as "
            "unobserved categorical values, not as evidence "
            "of equality or difference."
        ),
        "levels": levels,
    }


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Partial Observability Bounds v0.1"
    )
    lines.append("")

    lines.append(
        "Compatibility bounds for convergence under "
        "missing dependency attributes."
    )
    lines.append("")

    lines.append(
        "Unknown fields are treated as wildcards only "
        "for upper-bound calculations. No missing value "
        "is imputed as equal or different."
    )
    lines.append("")

    lines.append(
        "| Level | Complete | Largest group LB | "
        "Largest group UB | Ingredient span LB | "
        "Ingredient span UB | Certain cross-ingredient? | "
        "Possible cross-ingredient? |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|---:|---|---|"
    )

    for level_name, values in summary[
        "levels"
    ].items():
        group_bounds = values[
            "largest_group_bounds"
        ]

        span_bounds = values[
            "max_active_ingredient_span_bounds"
        ]

        lines.append(
            f"| `{level_name}` | "
            f"{values['n_complete']}/"
            f"{values['n_products']} "
            f"({_pct(values['complete_fraction'])}) | "
            f"{group_bounds['lower']} | "
            f"{group_bounds['upper']} | "
            f"{span_bounds['lower']} | "
            f"{span_bounds['upper']} | "
            f"{values['certain_cross_ingredient_convergence']} | "
            f"{values['possible_cross_ingredient_convergence']} |"
        )

    lines.append("")
    lines.append("## Upper-bound witnesses")
    lines.append("")

    for level_name, values in summary[
        "levels"
    ].items():
        lines.append(f"### {level_name}")
        lines.append("")

        group_witness = values[
            "largest_group_bounds"
        ]["upper_witness"]

        span_witness = values[
            "max_active_ingredient_span_bounds"
        ]["upper_witness"]

        lines.append(
            f"- Largest compatible group: "
            f"**{values['largest_group_bounds']['upper']}**"
        )

        if group_witness:
            lines.append(
                "- Compatible signature: "
                f"`{' | '.join(group_witness['signature'])}`"
            )

            lines.append(
                "- Products: "
                + ", ".join(
                    group_witness["product_ids"]
                )
            )

        lines.append(
            f"- Maximum compatible active-ingredient span: "
            f"**{values['max_active_ingredient_span_bounds']['upper']}**"
        )

        if span_witness:
            lines.append(
                "- Ingredients: "
                + ", ".join(
                    span_witness[
                        "active_ingredients"
                    ]
                )
            )

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute partial-observability convergence bounds."
        )
    )

    parser.add_argument("product_csv")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")

    args = parser.parse_args()

    summary = analyze_partial_observability(
        args.product_csv
    )

    markdown = render_markdown(summary)

    print(markdown)

    if args.json_out:
        output = Path(args.json_out)
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
        output = Path(args.md_out)
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