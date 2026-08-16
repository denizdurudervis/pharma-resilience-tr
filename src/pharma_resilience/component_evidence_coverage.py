from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from pharma_resilience.component_resolution import (
    build_resolution_analysis,
)


SCHEMA_VERSION = "component_evidence_coverage_v0_1"


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def build_product_universe(
    product_rows: list[dict[str, str]],
) -> dict[str, str]:
    """
    Return frozen product -> active ingredient mapping.

    The product audit defines the denominator universe.
    """

    mapping: dict[str, str] = {}

    for row in product_rows:
        product_id = (row.get("product_id") or "").strip()
        ingredient = (row.get("active_ingredient") or "").strip()

        if not product_id:
            continue

        if (
            product_id in mapping
            and mapping[product_id]
            and ingredient
            and mapping[product_id] != ingredient
        ):
            raise ValueError(
                f"Conflicting active ingredient for {product_id}"
            )

        mapping[product_id] = ingredient

    return mapping


def build_component_evidence_coverage(
    product_rows: list[dict[str, str]],
    component_rows: list[dict[str, str]],
) -> dict[str, Any]:

    product_to_ingredient = build_product_universe(
        product_rows
    )

    ingredients = sorted(
        {
            ingredient
            for ingredient in product_to_ingredient.values()
            if ingredient
        }
    )

    products_by_ingredient: dict[str, set[str]] = {
        ingredient: set()
        for ingredient in ingredients
    }

    for product_id, ingredient in product_to_ingredient.items():
        if ingredient:
            products_by_ingredient[ingredient].add(product_id)

    products_with_explicit_component: set[str] = {
        (row.get("product_id") or "").strip()
        for row in component_rows
        if (
            (row.get("observation_status") or "")
            .strip()
            .lower()
            == "explicit"
            and (row.get("component_class") or "").strip()
        )
    }

    ingredient_summary: dict[str, Any] = {}

    for ingredient in ingredients:
        total_products = products_by_ingredient[ingredient]

        observed_products = (
            total_products
            & products_with_explicit_component
        )

        unresolved_products = (
            total_products
            - observed_products
        )

        ingredient_summary[ingredient] = {
            "n_frozen_products": len(total_products),
            "frozen_product_ids": sorted(total_products),
            "n_products_with_any_explicit_component": len(
                observed_products
            ),
            "products_with_any_explicit_component": sorted(
                observed_products
            ),
            "n_products_without_explicit_component_evidence": len(
                unresolved_products
            ),
            "products_without_explicit_component_evidence": sorted(
                unresolved_products
            ),
        }

    resolution = build_resolution_analysis(
        component_rows
    )

    levels: dict[str, Any] = {}

    for level_name, level in resolution["levels"].items():

        products_by_component: dict[
            str,
            dict[str, set[str]],
        ] = defaultdict(
            lambda: defaultdict(set)
        )

        for edge in level["edges"]:
            product_id = edge["product_id"]
            component = edge["component_class"]

            ingredient = product_to_ingredient.get(
                product_id,
                "",
            )

            if not ingredient:
                continue

            products_by_component[
                component
            ][ingredient].add(product_id)

        component_results: dict[str, Any] = {}

        for component in sorted(
            level["component_nodes"]
        ):
            ingredient_results: dict[str, Any] = {}

            for ingredient in ingredients:
                n_total = len(
                    products_by_ingredient[ingredient]
                )

                n_observed_any = ingredient_summary[
                    ingredient
                ][
                    "n_products_with_any_explicit_component"
                ]

                n_unresolved_whole_product = (
                    ingredient_summary[
                        ingredient
                    ][
                        "n_products_without_explicit_component_evidence"
                    ]
                )

                documented_product_ids = sorted(
                    products_by_component[
                        component
                    ].get(
                        ingredient,
                        set(),
                    )
                )

                n_documented = len(
                    documented_product_ids
                )

                documented_share_frozen = (
                    n_documented / n_total
                    if n_total
                    else None
                )

                documented_share_observed = (
                    n_documented / n_observed_any
                    if n_observed_any
                    else None
                )

                unresolved_only_upper_scenario = (
                    min(
                        n_documented
                        + n_unresolved_whole_product,
                        n_total,
                    )
                    / n_total
                    if n_total
                    else None
                )

                ingredient_results[ingredient] = {
                    "n_frozen_products": n_total,
                    "n_products_with_any_explicit_component": (
                        n_observed_any
                    ),
                    "n_documented_with_component": (
                        n_documented
                    ),
                    "documented_product_ids": (
                        documented_product_ids
                    ),
                    "documented_share_frozen": round(
                        documented_share_frozen,
                        6,
                    )
                    if documented_share_frozen is not None
                    else None,
                    "documented_share_observed": round(
                        documented_share_observed,
                        6,
                    )
                    if documented_share_observed is not None
                    else None,
                    "unresolved_only_upper_scenario": round(
                        unresolved_only_upper_scenario,
                        6,
                    )
                    if unresolved_only_upper_scenario is not None
                    else None,
                }

            component_results[component] = {
                "component_class": component,
                "ingredients": ingredient_results,
            }

        levels[level_name] = {
            "n_component_classes": len(
                component_results
            ),
            "components": component_results,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "ingredients": ingredients,
        "ingredient_summary": ingredient_summary,
        "levels": levels,
        "interpretation": {
            "documented_share_frozen": (
                "Fraction of all frozen-sample products for an "
                "active ingredient with explicit documentary "
                "support for the component class."
            ),
            "documented_share_observed": (
                "Fraction among products having at least one "
                "explicit component observation."
            ),
            "unresolved_only_upper_scenario": (
                "Sensitivity scenario in which every product "
                "without any explicit component evidence is "
                "assumed to contain the component."
            ),
            "warning": (
                "These are evidence-support frequencies, not "
                "estimates of physical dependence prevalence. "
                "The upper scenario propagates fully unresolved "
                "products only and does not resolve component-"
                "specific omissions within otherwise observed "
                "documents."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("product_audit")
    parser.add_argument("component_audit")

    parser.add_argument(
        "--json-out",
        default=None,
    )

    args = parser.parse_args()

    product_rows = read_csv(
        args.product_audit
    )

    component_rows = read_csv(
        args.component_audit
    )

    analysis = build_component_evidence_coverage(
        product_rows,
        component_rows,
    )

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

    print("COMPONENT EVIDENCE COVERAGE")
    print()

    for ingredient, summary in analysis[
        "ingredient_summary"
    ].items():
        print(
            ingredient,
            "=> frozen=",
            summary["n_frozen_products"],
            "explicit-component products=",
            summary[
                "n_products_with_any_explicit_component"
            ],
            "without explicit component evidence=",
            summary[
                "n_products_without_explicit_component_evidence"
            ],
        )

    print()

    r2 = analysis["levels"]["R2_terminal"]

    for component in (
        "glass_vial",
        "rubber_stopper",
        "aluminium_cap",
    ):
        if component not in r2["components"]:
            continue

        print(component)

        for ingredient, values in r2[
            "components"
        ][component]["ingredients"].items():
            print(
                " ",
                ingredient,
                "documented=",
                values[
                    "n_documented_with_component"
                ],
                "/",
                values["n_frozen_products"],
                "frozen_share=",
                values[
                    "documented_share_frozen"
                ],
                "observed_share=",
                values[
                    "documented_share_observed"
                ],
                "unresolved-only upper=",
                values[
                    "unresolved_only_upper_scenario"
                ],
            )

        print()


if __name__ == "__main__":
    main()