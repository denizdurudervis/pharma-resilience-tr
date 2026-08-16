from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def compute_facility_robustness_bounds(
    resolved_site_graph: dict[str, Any],
) -> dict[str, Any]:
    facilities = resolved_site_graph[
        "resolved_entities"
    ]

    results: dict[str, dict[str, Any]] = {}

    for facility_id, facility in sorted(
        facilities.items()
    ):
        product_ids = facility[
            "product_ids"
        ]

        ingredients = facility[
            "active_ingredients"
        ]

        mandatory = bool(
            facility.get(
                "mandatory_product_dependency_established",
                False,
            )
        )

        if mandatory:
            product_lower = len(product_ids)
            ingredient_lower = len(ingredients)
        else:
            product_lower = 0
            ingredient_lower = 0

        product_upper = len(product_ids)
        ingredient_upper = len(ingredients)

        results[facility_id] = {
            "facility_id": facility_id,

            "product_impact_lower": (
                product_lower
            ),

            "product_impact_upper": (
                product_upper
            ),

            "product_impact_gap": (
                product_upper
                - product_lower
            ),

            "ingredient_impact_lower": (
                ingredient_lower
            ),

            "ingredient_impact_upper": (
                ingredient_upper
            ),

            "ingredient_impact_gap": (
                ingredient_upper
                - ingredient_lower
            ),

            "product_ids": product_ids,

            "active_ingredients": ingredients,

            "cross_ingredient_impact_certain": (
                ingredient_lower >= 2
            ),

            "cross_ingredient_impact_possible": (
                ingredient_upper >= 2
            ),

            "mandatory_dependence_established": (
                mandatory
            ),
        }

    informative = {
        facility_id: values
        for facility_id, values
        in results.items()
        if (
            values["product_impact_gap"] > 0
            or values["ingredient_impact_gap"] > 0
        )
    }

    possible_cross_ingredient = {
        facility_id: values
        for facility_id, values
        in results.items()
        if values[
            "cross_ingredient_impact_possible"
        ]
    }

    certain_cross_ingredient = {
        facility_id: values
        for facility_id, values
        in results.items()
        if values[
            "cross_ingredient_impact_certain"
        ]
    }

    max_product_upper = max(
        (
            values["product_impact_upper"]
            for values in results.values()
        ),
        default=0,
    )

    max_ingredient_upper = max(
        (
            values["ingredient_impact_upper"]
            for values in results.values()
        ),
        default=0,
    )

    return {
        "n_resolved_facilities": len(
            results
        ),

        "n_informative_facility_bounds": len(
            informative
        ),

        "n_possible_cross_ingredient_facilities": len(
            possible_cross_ingredient
        ),

        "n_certain_cross_ingredient_facilities": len(
            certain_cross_ingredient
        ),

        "max_possible_product_impact": (
            max_product_upper
        ),

        "max_possible_ingredient_impact": (
            max_ingredient_upper
        ),

        "facility_bounds": results,

        "possible_cross_ingredient_facilities": (
            possible_cross_ingredient
        ),

        "certain_cross_ingredient_facilities": (
            certain_cross_ingredient
        ),

        "interpretation": (
            "Lower bounds count only product impacts supported "
            "by established mandatory facility dependence. "
            "Upper bounds treat every observed product-facility "
            "edge as potentially mandatory. These are evidence "
            "bounds, not failure probabilities."
        ),
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Facility Robustness Bounds v0.1"
    )
    lines.append("")

    lines.append(
        "Evidence-bounded disruption analysis for manually "
        "resolved manufacturing facilities."
    )
    lines.append("")

    lines.append(
        "> Bounds represent what current public evidence "
        "can and cannot exclude; they are not estimated "
        "failure probabilities."
    )
    lines.append("")

    lines.append("## Summary")
    lines.append("")

    lines.append(
        f"- Resolved facilities: "
        f"**{summary['n_resolved_facilities']}**"
    )

    lines.append(
        "- Facilities with non-zero uncertainty gap: "
        f"**{summary['n_informative_facility_bounds']}**"
    )

    lines.append(
        "- Possible cross-ingredient facility impacts: "
        f"**{summary['n_possible_cross_ingredient_facilities']}**"
    )

    lines.append(
        "- Certain cross-ingredient facility impacts: "
        f"**{summary['n_certain_cross_ingredient_facilities']}**"
    )

    lines.append(
        "- Maximum possible affected products from one "
        f"resolved facility: "
        f"**{summary['max_possible_product_impact']}**"
    )

    lines.append(
        "- Maximum possible active-ingredient span from one "
        f"resolved facility: "
        f"**{summary['max_possible_ingredient_impact']}**"
    )

    lines.append("")
    lines.append("## Facility bounds")
    lines.append("")

    lines.append(
        "| Facility | Product impact | "
        "Ingredient impact | Possible cross-ingredient? |"
    )

    lines.append(
        "|---|---:|---:|---|"
    )

    for facility_id, values in summary[
        "facility_bounds"
    ].items():
        product_bound = (
            f"{values['product_impact_lower']}"
            f"–{values['product_impact_upper']}"
        )

        ingredient_bound = (
            f"{values['ingredient_impact_lower']}"
            f"–{values['ingredient_impact_upper']}"
        )

        lines.append(
            f"| `{facility_id}` | "
            f"{product_bound} | "
            f"{ingredient_bound} | "
            f"{values['cross_ingredient_impact_possible']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")

    lines.append(
        "A non-zero upper bound does not establish that "
        "facility loss would disable the associated products. "
        "It means that the available public evidence does not "
        "exclude mandatory dependence."
    )

    lines.append("")

    lines.append(
        "A zero lower bound reflects absence of proven "
        "mandatory dependence rather than evidence of "
        "operational redundancy."
    )

    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute lower and upper facility disruption "
            "bounds under partial observability."
        )
    )

    parser.add_argument(
        "resolved_site_json"
    )

    parser.add_argument(
        "--json-out"
    )

    parser.add_argument(
        "--md-out"
    )

    args = parser.parse_args()

    with open(
        args.resolved_site_json,
        encoding="utf-8",
    ) as handle:
        graph = json.load(handle)

    summary = compute_facility_robustness_bounds(
        graph
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