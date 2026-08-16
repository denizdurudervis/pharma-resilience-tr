from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .audit_summary import read_csv


UNKNOWN_VALUES = {
    "",
    "unknown",
    "indeterminate",
    "none",
    "na",
    "n/a",
}


LEVELS: dict[str, tuple[str, ...]] = {
    "R0_process": (
        "process_class",
    ),
    "R1_process_container": (
        "process_class",
        "container_class",
    ),
    "R2_process_container_closure": (
        "process_class",
        "container_class",
        "closure_class",
    ),
    "R3_process_container_closure_named_site": (
        "process_class",
        "container_class",
        "closure_class",
        "site_name",
    ),
}


def _canonical(value: str | None) -> str:
    value = (value or "").strip()

    if value.casefold() in UNKNOWN_VALUES:
        return "unknown"

    return value


def _fraction(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    return round(numerator / denominator, 4)


def signature_for_product(
    product: dict[str, str],
    fields: tuple[str, ...],
) -> str | None:
    values: list[str] = []

    for field in fields:
        value = _canonical(product.get(field))

        if value == "unknown":
            return None

        values.append(value)

    return "|".join(values)


def analyze_level(
    products: list[dict[str, str]],
    fields: tuple[str, ...],
) -> dict[str, Any]:
    groups: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    missing_product_ids: list[str] = []

    for product in products:
        signature = signature_for_product(
            product,
            fields,
        )

        if signature is None:
            missing_product_ids.append(
                (product.get("product_id") or "").strip()
            )
            continue

        groups[signature].append(product)

    group_summary: dict[str, dict[str, Any]] = {}

    for signature, rows in sorted(groups.items()):
        ingredients = sorted(
            {
                _canonical(row.get("active_ingredient"))
                for row in rows
            }
        )

        product_ids = sorted(
            (row.get("product_id") or "").strip()
            for row in rows
        )

        group_summary[signature] = {
            "n_products": len(rows),
            "product_ids": product_ids,
            "n_active_ingredients": len(ingredients),
            "active_ingredients": ingredients,
        }

    cross_ingredient_groups = {
        signature: values
        for signature, values in group_summary.items()
        if values["n_active_ingredients"] >= 2
    }

    n_input = len(products)
    n_observed = sum(
        values["n_products"]
        for values in group_summary.values()
    )

    return {
        "fields": list(fields),
        "n_input_products": n_input,
        "n_observed_products": n_observed,
        "n_missing_products": n_input - n_observed,
        "coverage_fraction": _fraction(
            n_observed,
            n_input,
        ),
        "n_signatures": len(group_summary),
        "largest_signature_group": max(
            (
                values["n_products"]
                for values in group_summary.values()
            ),
            default=0,
        ),
        "max_active_ingredient_span": max(
            (
                values["n_active_ingredients"]
                for values in group_summary.values()
            ),
            default=0,
        ),
        "n_cross_ingredient_signatures": len(
            cross_ingredient_groups
        ),
        "missing_product_ids": sorted(
            missing_product_ids
        ),
        "groups": group_summary,
        "cross_ingredient_groups": (
            cross_ingredient_groups
        ),
    }


def analyze_resolution_sensitivity(
    product_csv: str | Path,
) -> dict[str, Any]:
    products = read_csv(product_csv)

    available_case = {
        level_name: analyze_level(
            products,
            fields,
        )
        for level_name, fields in LEVELS.items()
    }

    r3_fields = LEVELS[
        "R3_process_container_closure_named_site"
    ]

    complete_case_products = [
        product
        for product in products
        if signature_for_product(
            product,
            r3_fields,
        )
        is not None
    ]

    complete_case = {
        level_name: analyze_level(
            complete_case_products,
            fields,
        )
        for level_name, fields in LEVELS.items()
    }

    trajectories: dict[
        str,
        dict[str, str | None],
    ] = {}

    for product in products:
        product_id = (
            product.get("product_id") or ""
        ).strip()

        trajectories[product_id] = {
            level_name: signature_for_product(
                product,
                fields,
            )
            for level_name, fields in LEVELS.items()
        }

    return {
        "n_products": len(products),
        "level_definitions": {
            level: list(fields)
            for level, fields in LEVELS.items()
        },
        "available_case": available_case,
        "complete_case_n_products": len(
            complete_case_products
        ),
        "complete_case_product_ids": sorted(
            (product.get("product_id") or "").strip()
            for product in complete_case_products
        ),
        "complete_case": complete_case,
        "product_trajectories": trajectories,
    }


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def _render_level_table(
    levels: dict[str, dict[str, Any]],
) -> list[str]:
    lines = [
        (
            "| Level | Observed | Coverage | "
            "Signatures | Largest group | "
            "Cross-ingredient signatures | "
            "Max ingredient span |"
        ),
        (
            "|---|---:|---:|---:|---:|---:|---:|"
        ),
    ]

    for level_name, values in levels.items():
        lines.append(
            f"| `{level_name}` | "
            f"{values['n_observed_products']}/"
            f"{values['n_input_products']} | "
            f"{_pct(values['coverage_fraction'])} | "
            f"{values['n_signatures']} | "
            f"{values['largest_signature_group']} | "
            f"{values['n_cross_ingredient_signatures']} | "
            f"{values['max_active_ingredient_span']} |"
        )

    return lines


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Resolution Sensitivity v0.1"
    )
    lines.append("")
    lines.append(
        "Multiresolution convergence analysis "
        "for the frozen pharmaceutical audit sample."
    )
    lines.append("")
    lines.append(
        "R3 uses the named production site reported "
        "in public documents. It does not establish "
        "site role or site-list exhaustiveness."
    )
    lines.append("")

    lines.append("## Available-case analysis")
    lines.append("")
    lines.extend(
        _render_level_table(
            summary["available_case"]
        )
    )
    lines.append("")

    lines.append(
        "## Complete-case resolution sensitivity"
    )
    lines.append("")
    lines.append(
        "The complete-case panel fixes the product "
        "set to products observable at R3, preventing "
        "changes in missingness from being mistaken "
        "for changes caused by resolution."
    )
    lines.append("")
    lines.append(
        f"- Complete-case products: "
        f"**{summary['complete_case_n_products']}/"
        f"{summary['n_products']}**"
    )
    lines.append("")

    lines.extend(
        _render_level_table(
            summary["complete_case"]
        )
    )
    lines.append("")

    lines.append(
        "## Cross-ingredient convergence by resolution"
    )
    lines.append("")

    for level_name, level in summary[
        "available_case"
    ].items():
        lines.append(f"### {level_name}")
        lines.append("")

        shared = level[
            "cross_ingredient_groups"
        ]

        if not shared:
            lines.append(
                "No observed signature spans "
                "multiple active ingredients."
            )
            lines.append("")
            continue

        for signature, values in shared.items():
            ingredients = ", ".join(
                values["active_ingredients"]
            )

            lines.append(
                f"- `{signature}`: "
                f"{values['n_products']} products; "
                f"{values['n_active_ingredients']} "
                f"active ingredients "
                f"({ingredients})"
            )

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze convergence across nested "
            "pharmaceutical supply-route resolutions."
        )
    )

    parser.add_argument("product_csv")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")

    args = parser.parse_args()

    summary = analyze_resolution_sensitivity(
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