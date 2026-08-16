from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
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


DEPENDENCY_FIELDS = {
    "process": "process_class",
    "container": "container_class",
    "closure": "closure_class",
}


def _canonical(value: str | None) -> str:
    value = (value or "").strip()

    if value.casefold() in UNKNOWN_VALUES:
        return "unknown"

    return value


def _is_known(value: str | None) -> bool:
    return _canonical(value) != "unknown"


def _dependency_id(
    dependency_type: str,
    value: str,
) -> str:
    return f"{dependency_type}::{value}"


def build_dependency_graph(
    product_csv: str | Path,
    evidence_csv: str | Path,
) -> dict[str, Any]:
    products = read_csv(product_csv)
    evidence = read_csv(evidence_csv)

    product_nodes: dict[str, dict[str, Any]] = {}

    dependency_nodes: dict[str, dict[str, Any]] = {}

    edges: list[dict[str, str]] = []

    missing_by_type: dict[str, list[str]] = defaultdict(list)

    product_dependencies: dict[
        str,
        set[str],
    ] = defaultdict(set)

    for product in products:
        product_id = (
            product.get("product_id") or ""
        ).strip()

        product_nodes[product_id] = {
            "node_id": product_id,
            "node_type": "product",
            "product_name": (
                product.get("product_name") or ""
            ).strip(),
            "active_ingredient": _canonical(
                product.get("active_ingredient")
            ),
            "clinical_family": _canonical(
                product.get("clinical_family")
            ),
        }

        for dependency_type, field_name in (
            DEPENDENCY_FIELDS.items()
        ):
            value = _canonical(
                product.get(field_name)
            )

            if value == "unknown":
                missing_by_type[
                    dependency_type
                ].append(product_id)
                continue

            node_id = _dependency_id(
                dependency_type,
                value,
            )

            dependency_nodes[node_id] = {
                "node_id": node_id,
                "node_type": "dependency",
                "dependency_type": dependency_type,
                "value": value,
            }

            edge = {
                "product_id": product_id,
                "dependency_id": node_id,
                "dependency_type": dependency_type,
                "relation": "requires_observed",
                "source": "product_audit",
            }

            edges.append(edge)

            product_dependencies[
                product_id
            ].add(node_id)

    site_edges_seen: set[
        tuple[str, str]
    ] = set()

    products_with_observed_site: set[str] = set()

    for row in evidence:
        if (
            (row.get("field_name") or "").strip()
            != "manufacturing_site"
        ):
            continue

        field_present = (
            row.get("field_present") or ""
        ).strip().casefold()

        if field_present not in {
            "1",
            "true",
            "yes",
        }:
            continue

        site_value = _canonical(
            row.get("observed_value")
        )

        if site_value == "unknown":
            continue

        product_id = (
            row.get("product_id") or ""
        ).strip()

        if product_id not in product_nodes:
            continue

        products_with_observed_site.add(
            product_id
        )

        site_id = _dependency_id(
            "site",
            site_value,
        )

        dependency_nodes[site_id] = {
            "node_id": site_id,
            "node_type": "dependency",
            "dependency_type": "site",
            "value": site_value,
        }

        pair = (
            product_id,
            site_id,
        )

        if pair in site_edges_seen:
            continue

        site_edges_seen.add(pair)

        edges.append(
            {
                "product_id": product_id,
                "dependency_id": site_id,
                "dependency_type": "site",
                "relation": "observed_named_site",
                "source": "evidence_audit",
            }
        )

        product_dependencies[
            product_id
        ].add(site_id)

    for product_id in product_nodes:
        if (
            product_id
            not in products_with_observed_site
        ):
            missing_by_type["site"].append(
                product_id
            )

    dependency_products: dict[
        str,
        set[str],
    ] = defaultdict(set)

    dependency_ingredients: dict[
        str,
        set[str],
    ] = defaultdict(set)

    for edge in edges:
        product_id = edge["product_id"]
        dependency_id = edge["dependency_id"]

        dependency_products[
            dependency_id
        ].add(product_id)

        ingredient = product_nodes[
            product_id
        ]["active_ingredient"]

        dependency_ingredients[
            dependency_id
        ].add(ingredient)

    shared_dependencies: dict[
        str,
        dict[str, Any],
    ] = {}

    cross_ingredient_dependencies: dict[
        str,
        dict[str, Any],
    ] = {}

    for dependency_id in sorted(
        dependency_nodes
    ):
        products_here = sorted(
            dependency_products[
                dependency_id
            ]
        )

        ingredients_here = sorted(
            dependency_ingredients[
                dependency_id
            ]
        )

        if len(products_here) >= 2:
            shared_dependencies[
                dependency_id
            ] = {
                "dependency_type": (
                    dependency_nodes[
                        dependency_id
                    ]["dependency_type"]
                ),
                "value": (
                    dependency_nodes[
                        dependency_id
                    ]["value"]
                ),
                "n_products": len(
                    products_here
                ),
                "product_ids": products_here,
                "n_active_ingredients": len(
                    ingredients_here
                ),
                "active_ingredients": (
                    ingredients_here
                ),
            }

        if len(ingredients_here) >= 2:
            cross_ingredient_dependencies[
                dependency_id
            ] = {
                "dependency_type": (
                    dependency_nodes[
                        dependency_id
                    ]["dependency_type"]
                ),
                "value": (
                    dependency_nodes[
                        dependency_id
                    ]["value"]
                ),
                "n_products": len(
                    products_here
                ),
                "product_ids": products_here,
                "n_active_ingredients": len(
                    ingredients_here
                ),
                "active_ingredients": (
                    ingredients_here
                ),
            }

    dependency_type_counts = Counter(
        node["dependency_type"]
        for node in dependency_nodes.values()
    )

    edge_type_counts = Counter(
        edge["dependency_type"]
        for edge in edges
    )

    return {
        "n_product_nodes": len(
            product_nodes
        ),
        "n_dependency_nodes": len(
            dependency_nodes
        ),
        "n_edges": len(edges),

        "dependency_node_counts": dict(
            sorted(
                dependency_type_counts.items()
            )
        ),

        "edge_counts": dict(
            sorted(
                edge_type_counts.items()
            )
        ),

        "product_nodes": product_nodes,
        "dependency_nodes": dependency_nodes,
        "edges": edges,

        "product_dependencies": {
            product_id: sorted(
                dependencies
            )
            for product_id, dependencies
            in sorted(
                product_dependencies.items()
            )
        },

        "missing_by_dependency_type": {
            dependency_type: sorted(
                set(product_ids)
            )
            for dependency_type, product_ids
            in sorted(
                missing_by_type.items()
            )
        },

        "shared_dependencies": (
            shared_dependencies
        ),

        "cross_ingredient_dependencies": (
            cross_ingredient_dependencies
        ),
    }


def render_markdown(
    graph: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Product–Dependency Graph v0.1"
    )
    lines.append("")

    lines.append(
        "Observed dependency graph for the frozen "
        "pharmaceutical audit sample."
    )
    lines.append("")

    lines.append(
        "Unknown dependency attributes are omitted "
        "from the graph rather than represented by "
        "a shared unknown node."
    )
    lines.append("")

    lines.append("## Graph size")
    lines.append("")
    lines.append(
        f"- Product nodes: "
        f"**{graph['n_product_nodes']}**"
    )
    lines.append(
        f"- Dependency nodes: "
        f"**{graph['n_dependency_nodes']}**"
    )
    lines.append(
        f"- Observed edges: "
        f"**{graph['n_edges']}**"
    )
    lines.append("")

    lines.append(
        "## Dependency nodes by type"
    )
    lines.append("")

    for dependency_type, count in graph[
        "dependency_node_counts"
    ].items():
        lines.append(
            f"- `{dependency_type}`: {count}"
        )

    lines.append("")
    lines.append(
        "## Missing dependency observations"
    )
    lines.append("")

    for dependency_type, product_ids in graph[
        "missing_by_dependency_type"
    ].items():
        lines.append(
            f"- `{dependency_type}`: "
            f"{len(product_ids)} products"
        )

    lines.append("")
    lines.append(
        "## Cross-ingredient shared dependencies"
    )
    lines.append("")

    shared = graph[
        "cross_ingredient_dependencies"
    ]

    if not shared:
        lines.append(
            "No observed dependency node is shared "
            "across multiple active ingredients."
        )
    else:
        lines.append(
            "| Type | Dependency | Products | "
            "Active ingredients | Ingredients |"
        )
        lines.append(
            "|---|---|---:|---:|---|"
        )

        for values in shared.values():
            ingredients = ", ".join(
                values[
                    "active_ingredients"
                ]
            )

            lines.append(
                f"| `{values['dependency_type']}` | "
                f"`{values['value']}` | "
                f"{values['n_products']} | "
                f"{values['n_active_ingredients']} | "
                f"{ingredients} |"
            )

    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build the observed pharmaceutical "
            "product-dependency graph."
        )
    )

    parser.add_argument("product_csv")
    parser.add_argument("evidence_csv")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")

    args = parser.parse_args()

    graph = build_dependency_graph(
        args.product_csv,
        args.evidence_csv,
    )

    markdown = render_markdown(graph)

    print(markdown)

    if args.json_out:
        output = Path(args.json_out)
        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                graph,
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