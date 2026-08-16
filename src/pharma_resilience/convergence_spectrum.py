from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict[str, Any]:
    with open(
        path,
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def is_placeholder_dependency(
    dependency_type: str,
    value: str,
) -> bool:
    value_norm = (
        value.strip()
        .casefold()
        .replace("-", "_")
        .replace(" ", "_")
    )

    if value_norm == "unknown":
        return True

    if value_norm.startswith(
        "not_applicable"
    ):
        return True

    if value_norm in {
        "",
        "na",
        "n/a",
        "none",
        "missing",
    }:
        return True

    return False


def build_convergence_spectrum(
    graph: dict[str, Any],
) -> dict[str, Any]:

    product_nodes = graph[
        "product_nodes"
    ]

    dependency_nodes = graph[
        "dependency_nodes"
    ]

    product_dependencies = graph[
        "product_dependencies"
    ]

    dependency_to_products: dict[
        str,
        set[str],
    ] = defaultdict(set)

    for product_id, dependencies in (
        product_dependencies.items()
    ):
        for dependency_id in dependencies:
            dependency_to_products[
                dependency_id
            ].add(product_id)

    records: list[dict[str, Any]] = []

    for dependency_id, dependency in sorted(
        dependency_nodes.items()
    ):
        dependency_type = dependency[
            "dependency_type"
        ]

        value = dependency[
            "value"
        ]

        product_ids = sorted(
            dependency_to_products.get(
                dependency_id,
                set(),
            )
        )

        active_ingredients = sorted(
            {
                product_nodes[
                    product_id
                ]["active_ingredient"]
                for product_id
                in product_ids
                if product_nodes[
                    product_id
                ].get(
                    "active_ingredient"
                )
            }
        )

        clinical_families = sorted(
            {
                product_nodes[
                    product_id
                ].get(
                    "clinical_family",
                    "",
                )
                for product_id
                in product_ids
                if product_nodes[
                    product_id
                ].get(
                    "clinical_family"
                )
            }
        )

        n_products = len(
            product_ids
        )

        n_active_ingredients = len(
            active_ingredients
        )

        placeholder = (
            is_placeholder_dependency(
                dependency_type,
                value,
            )
        )

        shared_across_products = (
            n_products >= 2
        )

        cross_ingredient = (
            n_active_ingredients >= 2
        )

        informative_cross_ingredient = (
            cross_ingredient
            and not placeholder
        )

        products_per_ingredient = (
            n_products
            / n_active_ingredients
            if n_active_ingredients
            else None
        )

        ingredient_fraction = (
            n_active_ingredients
            / n_products
            if n_products
            else None
        )

        records.append(
            {
                "dependency_id": (
                    dependency_id
                ),
                "dependency_type": (
                    dependency_type
                ),
                "value": value,
                "placeholder": (
                    placeholder
                ),
                "n_products": (
                    n_products
                ),
                "product_ids": (
                    product_ids
                ),
                "n_active_ingredients": (
                    n_active_ingredients
                ),
                "active_ingredients": (
                    active_ingredients
                ),
                "n_clinical_families": len(
                    clinical_families
                ),
                "clinical_families": (
                    clinical_families
                ),
                "shared_across_products": (
                    shared_across_products
                ),
                "cross_ingredient": (
                    cross_ingredient
                ),
                "informative_cross_ingredient": (
                    informative_cross_ingredient
                ),
                "products_per_ingredient": (
                    products_per_ingredient
                ),
                "ingredient_fraction": (
                    ingredient_fraction
                ),
            }
        )

    records.sort(
        key=lambda row: (
            -int(
                row[
                    "informative_cross_ingredient"
                ]
            ),
            -row[
                "n_active_ingredients"
            ],
            -row[
                "n_products"
            ],
            row[
                "dependency_type"
            ],
            row[
                "value"
            ],
        )
    )

    by_type: dict[
        str,
        dict[str, Any],
    ] = {}

    dependency_types = sorted(
        {
            row[
                "dependency_type"
            ]
            for row in records
        }
    )

    for dependency_type in dependency_types:
        subset = [
            row
            for row in records
            if row[
                "dependency_type"
            ]
            == dependency_type
        ]

        non_placeholder = [
            row
            for row in subset
            if not row[
                "placeholder"
            ]
        ]

        shared = [
            row
            for row in non_placeholder
            if row[
                "shared_across_products"
            ]
        ]

        cross = [
            row
            for row in non_placeholder
            if row[
                "cross_ingredient"
            ]
        ]

        by_type[
            dependency_type
        ] = {
            "n_nodes": len(
                subset
            ),
            "n_non_placeholder_nodes": len(
                non_placeholder
            ),
            "n_shared_nodes": len(
                shared
            ),
            "n_cross_ingredient_nodes": len(
                cross
            ),
            "cross_ingredient_node_ids": [
                row[
                    "dependency_id"
                ]
                for row in cross
            ],
        }

    informative_cross = [
        row
        for row in records
        if row[
            "informative_cross_ingredient"
        ]
    ]

    shared_non_cross = [
        row
        for row in records
        if (
            not row[
                "placeholder"
            ]
            and row[
                "shared_across_products"
            ]
            and not row[
                "cross_ingredient"
            ]
        )
    ]

    placeholder_records = [
        row
        for row in records
        if row[
            "placeholder"
        ]
    ]

    return {
        "n_products": len(
            product_nodes
        ),
        "n_dependency_nodes": len(
            dependency_nodes
        ),
        "n_non_placeholder_nodes": sum(
            not row[
                "placeholder"
            ]
            for row in records
        ),
        "n_placeholder_nodes": len(
            placeholder_records
        ),
        "n_shared_non_placeholder_nodes": sum(
            (
                not row[
                    "placeholder"
                ]
                and row[
                    "shared_across_products"
                ]
            )
            for row in records
        ),
        "n_informative_cross_ingredient_nodes": len(
            informative_cross
        ),
        "by_dependency_type": (
            by_type
        ),
        "informative_cross_ingredient_nodes": (
            informative_cross
        ),
        "shared_single_ingredient_nodes": (
            shared_non_cross
        ),
        "placeholder_nodes": (
            placeholder_records
        ),
        "all_nodes": records,
        "interpretation": (
            "The spectrum exhaustively scans every dependency "
            "node in the observed graph. Cross-ingredient "
            "convergence is defined descriptively as a "
            "non-placeholder dependency node observed for "
            "products from at least two active ingredients. "
            "This does not establish technological "
            "indispensability, mandatory dependence, or a "
            "common failure mode."
        ),
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:

    lines: list[str] = []

    lines.append(
        "# Dependency Convergence Spectrum v0.1"
    )
    lines.append("")

    lines.append(
        "Exhaustive node-level scan of the frozen "
        "observed pharmaceutical dependency graph."
    )
    lines.append("")

    lines.append(
        "> Cross-ingredient convergence is descriptive. "
        "It is not evidence of mandatory dependence or "
        "common-mode failure."
    )
    lines.append("")

    lines.append(
        "## Graph coverage"
    )
    lines.append("")

    lines.append(
        f"- Products: "
        f"**{summary['n_products']}**"
    )

    lines.append(
        f"- Dependency nodes scanned: "
        f"**{summary['n_dependency_nodes']}**"
    )

    lines.append(
        f"- Non-placeholder nodes: "
        f"**{summary['n_non_placeholder_nodes']}**"
    )

    lines.append(
        f"- Placeholder nodes: "
        f"**{summary['n_placeholder_nodes']}**"
    )

    lines.append(
        "- Shared non-placeholder nodes: "
        f"**{summary['n_shared_non_placeholder_nodes']}**"
    )

    lines.append(
        "- Informative cross-ingredient nodes: "
        f"**{summary['n_informative_cross_ingredient_nodes']}**"
    )

    lines.append("")
    lines.append(
        "## By dependency type"
    )
    lines.append("")

    lines.append(
        "| Type | Nodes | Non-placeholder | "
        "Shared | Cross-ingredient |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|"
    )

    for dependency_type, values in summary[
        "by_dependency_type"
    ].items():
        lines.append(
            f"| `{dependency_type}` | "
            f"{values['n_nodes']} | "
            f"{values['n_non_placeholder_nodes']} | "
            f"{values['n_shared_nodes']} | "
            f"{values['n_cross_ingredient_nodes']} |"
        )

    lines.append("")
    lines.append(
        "## Informative cross-ingredient nodes"
    )
    lines.append("")

    informative = summary[
        "informative_cross_ingredient_nodes"
    ]

    if not informative:
        lines.append(
            "No informative cross-ingredient "
            "dependency nodes were observed."
        )
    else:
        lines.append(
            "| Node | Type | Products | "
            "Active ingredients | Ingredients |"
        )

        lines.append(
            "|---|---|---:|---:|---|"
        )

        for row in informative:
            ingredients = ", ".join(
                row[
                    "active_ingredients"
                ]
            )

            lines.append(
                f"| `{row['dependency_id']}` | "
                f"`{row['dependency_type']}` | "
                f"{row['n_products']} | "
                f"{row['n_active_ingredients']} | "
                f"{ingredients} |"
            )

    lines.append("")
    lines.append(
        "## Interpretation"
    )
    lines.append("")

    lines.append(
        "Because every dependency node is evaluated under "
        "the same pre-specified rule, nodes reported above "
        "are not manually selected examples from the graph."
    )

    lines.append("")

    lines.append(
        "Placeholder observations such as `unknown` and "
        "`not_applicable...` are retained for auditability "
        "but excluded from substantive convergence counts."
    )

    lines.append("")

    return "\n".join(
        lines
    )


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Exhaustively scan dependency nodes for "
            "cross-product and cross-ingredient convergence."
        )
    )

    parser.add_argument(
        "dependency_graph"
    )

    parser.add_argument(
        "--json-out"
    )

    parser.add_argument(
        "--md-out"
    )

    args = parser.parse_args()

    graph = load_json(
        args.dependency_graph
    )

    summary = build_convergence_spectrum(
        graph
    )

    markdown = render_markdown(
        summary
    )

    print(
        markdown
    )

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