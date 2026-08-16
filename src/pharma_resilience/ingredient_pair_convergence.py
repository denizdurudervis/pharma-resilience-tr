from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from pharma_resilience.component_resolution import (
    build_resolution_analysis,
    read_component_audit,
)


SCHEMA_VERSION = "ingredient_pair_convergence_v0_1"


def build_product_ingredient_map(
    rows: list[dict[str, str]],
) -> dict[str, str]:
    """
    Build a unique product -> active ingredient mapping.

    Conflicting non-empty ingredient assignments for the same product
    are rejected rather than silently resolved.
    """

    observed: dict[str, set[str]] = {}

    for row in rows:
        product_id = (row.get("product_id") or "").strip()
        ingredient = (row.get("active_ingredient") or "").strip()

        if not product_id:
            continue

        observed.setdefault(product_id, set())

        if ingredient:
            observed[product_id].add(ingredient)

    result: dict[str, str] = {}

    for product_id, ingredients in observed.items():
        if len(ingredients) > 1:
            raise ValueError(
                f"Conflicting active ingredients for "
                f"{product_id}: {sorted(ingredients)}"
            )

        result[product_id] = (
            next(iter(ingredients))
            if ingredients
            else ""
        )

    return result


def ingredient_component_sets(
    rows: list[dict[str, str]],
    resolution_analysis: dict[str, Any],
) -> dict[str, dict[str, set[str]]]:
    """
    For each resolution level, return the set of observed physical
    component classes associated with each active ingredient.

    Sets are unweighted by product count. This is a structural
    ingredient-level convergence representation, not yet a measure of
    mandatory dependence or disruption probability.
    """

    product_to_ingredient = build_product_ingredient_map(rows)

    ingredients = sorted(
        {
            ingredient
            for ingredient in product_to_ingredient.values()
            if ingredient
        }
    )

    output: dict[str, dict[str, set[str]]] = {}

    for level, result in resolution_analysis["levels"].items():
        sets = {
            ingredient: set()
            for ingredient in ingredients
        }

        for edge in result["edges"]:
            product_id = edge["product_id"]
            ingredient = product_to_ingredient.get(product_id, "")

            if not ingredient:
                continue

            sets[ingredient].add(
                edge["component_class"]
            )

        output[level] = sets

    return output


def pair_id(a: str, b: str) -> str:
    left, right = sorted((a, b))
    return f"{left}__{right}"


def build_pair_convergence(
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    resolution = build_resolution_analysis(rows)

    component_sets = ingredient_component_sets(
        rows,
        resolution,
    )

    all_ingredients = sorted(
        {
            ingredient
            for level_sets in component_sets.values()
            for ingredient in level_sets
        }
    )

    level_results: dict[str, Any] = {}

    previous_counts: dict[str, int] | None = None

    for level in (
        "R0_exact",
        "R1_parent",
        "R2_terminal",
    ):
        sets = component_sets[level]

        pairs: list[dict[str, Any]] = []
        current_counts: dict[str, int] = {}

        for ingredient_a, ingredient_b in combinations(
            all_ingredients,
            2,
        ):
            components_a = sets[ingredient_a]
            components_b = sets[ingredient_b]

            shared = components_a & components_b
            union = components_a | components_b

            pid = pair_id(
                ingredient_a,
                ingredient_b,
            )

            n_shared = len(shared)
            current_counts[pid] = n_shared

            if previous_counts is None:
                delta = None
            else:
                delta = (
                    n_shared
                    - previous_counts[pid]
                )

            jaccard = (
                len(shared) / len(union)
                if union
                else None
            )

            pairs.append(
                {
                    "pair_id": pid,
                    "ingredient_a": ingredient_a,
                    "ingredient_b": ingredient_b,
                    "n_components_a": len(
                        components_a
                    ),
                    "n_components_b": len(
                        components_b
                    ),
                    "n_shared_components": n_shared,
                    "shared_component_classes": sorted(
                        shared
                    ),
                    "n_union_components": len(union),
                    "jaccard": (
                        round(jaccard, 6)
                        if jaccard is not None
                        else None
                    ),
                    "delta_shared_from_previous_resolution": (
                        delta
                    ),
                }
            )

        pairs.sort(
            key=lambda item: (
                -item["n_shared_components"],
                item["ingredient_a"],
                item["ingredient_b"],
            )
        )

        shared_counts = [
            item["n_shared_components"]
            for item in pairs
        ]

        level_results[level] = {
            "n_ingredients": len(all_ingredients),
            "n_pairs": len(pairs),
            "n_pairs_with_shared_components": sum(
                value > 0
                for value in shared_counts
            ),
            "mean_shared_component_count": round(
                sum(shared_counts)
                / len(shared_counts),
                6,
            )
            if shared_counts
            else 0.0,
            "max_shared_component_count": (
                max(shared_counts)
                if shared_counts
                else 0
            ),
            "pairs": pairs,
        }

        previous_counts = current_counts

    return {
        "schema_version": SCHEMA_VERSION,
        "ingredients": all_ingredients,
        "n_ingredients": len(all_ingredients),
        "levels": level_results,
        "interpretation": {
            "unit": "active-ingredient pair",
            "meaning": (
                "Number of observed physical component classes "
                "shared by two active ingredients at each "
                "dependency-resolution level."
            ),
            "not_established": [
                "supplier identity",
                "mandatory dependence",
                "non-substitutability",
                "common failure mode",
                "disruption probability",
            ],
        },
    }


def render_markdown(
    analysis: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Active-Ingredient Pair Component Convergence v0.1"
    )
    lines.append("")

    lines.append(
        "Pairwise structural overlap in observed pharmaceutical "
        "component classes across dependency-resolution levels."
    )
    lines.append("")

    lines.append(
        "**Interpretation:** a shared component class indicates "
        "observed component-level convergence. It does not by itself "
        "establish common suppliers, mandatory dependence, "
        "non-substitutability, or a common failure mode."
    )
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| Level | Ingredient pairs | Pairs with overlap | "
        "Mean shared components | Maximum |"
    )
    lines.append("|---|---:|---:|---:|---:|")

    for level, result in analysis["levels"].items():
        lines.append(
            f"| `{level}` | "
            f"{result['n_pairs']} | "
            f"{result['n_pairs_with_shared_components']} | "
            f"{result['mean_shared_component_count']:.3f} | "
            f"{result['max_shared_component_count']} |"
        )

    lines.append("")

    for level, result in analysis["levels"].items():
        lines.append(f"## {level}")
        lines.append("")
        lines.append(
            "| Ingredient pair | Shared components | "
            "Jaccard | Delta from previous level | Components |"
        )
        lines.append("|---|---:|---:|---:|---|")

        for pair in result["pairs"]:
            shared = ", ".join(
                f"`{item}`"
                for item in pair[
                    "shared_component_classes"
                ]
            )

            delta = pair[
                "delta_shared_from_previous_resolution"
            ]

            delta_text = (
                "NA"
                if delta is None
                else str(delta)
            )

            lines.append(
                f"| {pair['ingredient_a']} – "
                f"{pair['ingredient_b']} | "
                f"{pair['n_shared_components']} | "
                f"{pair['jaccard']:.3f} | "
                f"{delta_text} | "
                f"{shared} |"
            )

        lines.append("")

    lines.append("## Methodological note")
    lines.append("")
    lines.append(
        "The analysis uses presence/absence sets at the active-ingredient "
        "level. Multiple products containing the same active ingredient "
        "therefore expand the ingredient's observed component set but do "
        "not directly weight a component by the number of products."
    )
    lines.append("")
    lines.append(
        "Product-level redundancy and evidence-bounded disruption "
        "analysis are separate downstream tasks."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "component_audit",
    )

    parser.add_argument(
        "--json-out",
        default=None,
    )

    parser.add_argument(
        "--md-out",
        default=None,
    )

    args = parser.parse_args()

    rows = read_component_audit(
        args.component_audit
    )

    analysis = build_pair_convergence(rows)

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with out.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                analysis,
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")

    if args.md_out:
        out = Path(args.md_out)
        out.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        out.write_text(
            render_markdown(analysis),
            encoding="utf-8",
        )

    print("INGREDIENT-PAIR COMPONENT CONVERGENCE")
    print()
    print(
        "ingredients =",
        analysis["ingredients"],
    )
    print()

    for level, result in analysis["levels"].items():
        print(level)
        print(
            "  pairs =",
            result["n_pairs"],
        )
        print(
            "  pairs with shared components =",
            result[
                "n_pairs_with_shared_components"
            ],
        )
        print(
            "  mean shared component count =",
            result[
                "mean_shared_component_count"
            ],
        )
        print(
            "  max shared component count =",
            result[
                "max_shared_component_count"
            ],
        )

        for pair in result["pairs"]:
            print(
                " ",
                pair["ingredient_a"],
                "<->",
                pair["ingredient_b"],
                "shared=",
                pair["n_shared_components"],
                pair["shared_component_classes"],
                "delta=",
                pair[
                    "delta_shared_from_previous_resolution"
                ],
            )

        print()


if __name__ == "__main__":
    main()