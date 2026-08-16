from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "component_graph_v0_1"


def read_component_audit(path: str | Path) -> list[dict[str, str]]:
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})


def build_component_graph(rows: list[dict[str, str]]) -> dict[str, Any]:
    """
    Build a physical product-component graph from the frozen component audit.

    Important semantics
    -------------------
    - Only explicit observations with a non-empty component_class create
      component edges.
    - Unresolved products remain in the product universe and coverage
      statistics, but no component dependency is imputed for them.
    - Component identity is physical component_class.
    - component_role is retained on the product-component relationship.
      Therefore, the same physical component may occupy multiple roles.
    - Observed convergence is descriptive. It does not establish supplier
      identity, non-substitutability, mandatory dependence, or a common
      failure mode.
    """

    product_nodes: dict[str, dict[str, Any]] = {}

    component_acc: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "product_ids": set(),
            "active_ingredients": set(),
            "roles": set(),
            "parent_component_classes": set(),
            "source_document_ids": set(),
            "raw_source_wordings": set(),
        }
    )

    edge_acc: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "roles": set(),
            "parent_component_classes": set(),
            "source_document_ids": set(),
            "raw_source_wordings": set(),
        }
    )

    explicit_observation_count = 0
    unresolved_product_ids: set[str] = set()

    for row in rows:
        product_id = (row.get("product_id") or "").strip()
        if not product_id:
            continue

        product_nodes.setdefault(
            product_id,
            {
                "product_id": product_id,
                "product_name": (row.get("product_name") or "").strip(),
                "active_ingredient": (row.get("active_ingredient") or "").strip(),
            },
        )

        status = (row.get("observation_status") or "").strip().lower()
        component_class = (row.get("component_class") or "").strip()

        if status == "unresolved":
            unresolved_product_ids.add(product_id)

        if status != "explicit" or not component_class:
            continue

        explicit_observation_count += 1

        role = (row.get("component_role") or "").strip()
        parent = (row.get("parent_component_class") or "").strip()
        source_document_id = (row.get("source_document_id") or "").strip()
        raw_wording = (row.get("raw_source_wording") or "").strip()
        active_ingredient = (
            product_nodes[product_id].get("active_ingredient") or ""
        ).strip()

        component = component_acc[component_class]
        component["product_ids"].add(product_id)
        if active_ingredient:
            component["active_ingredients"].add(active_ingredient)
        if role:
            component["roles"].add(role)
        if parent:
            component["parent_component_classes"].add(parent)
        if source_document_id:
            component["source_document_ids"].add(source_document_id)
        if raw_wording:
            component["raw_source_wordings"].add(raw_wording)

        edge = edge_acc[(product_id, component_class)]
        if role:
            edge["roles"].add(role)
        if parent:
            edge["parent_component_classes"].add(parent)
        if source_document_id:
            edge["source_document_ids"].add(source_document_id)
        if raw_wording:
            edge["raw_source_wordings"].add(raw_wording)

    component_nodes: dict[str, dict[str, Any]] = {}

    for component_class, values in component_acc.items():
        product_ids = sorted(values["product_ids"])
        active_ingredients = sorted(values["active_ingredients"])

        component_nodes[component_class] = {
            "component_class": component_class,
            "n_products": len(product_ids),
            "product_ids": product_ids,
            "n_active_ingredients": len(active_ingredients),
            "active_ingredients": active_ingredients,
            "roles": sorted(values["roles"]),
            "parent_component_classes": sorted(
                values["parent_component_classes"]
            ),
            "source_document_ids": sorted(values["source_document_ids"]),
            "raw_source_wordings": sorted(values["raw_source_wordings"]),
        }

    edges: list[dict[str, Any]] = []

    for (product_id, component_class), values in sorted(edge_acc.items()):
        edges.append(
            {
                "product_id": product_id,
                "component_class": component_class,
                "roles": sorted(values["roles"]),
                "parent_component_classes": sorted(
                    values["parent_component_classes"]
                ),
                "source_document_ids": sorted(values["source_document_ids"]),
                "raw_source_wordings": sorted(values["raw_source_wordings"]),
            }
        )

    shared_components = {
        key: value
        for key, value in component_nodes.items()
        if value["n_products"] >= 2
    }

    cross_ingredient_components = {
        key: value
        for key, value in component_nodes.items()
        if value["n_active_ingredients"] >= 2
    }

    observed_product_ids = sorted(
        {
            edge["product_id"]
            for edge in edges
        }
    )

    all_product_ids = sorted(product_nodes)

    return {
        "schema_version": SCHEMA_VERSION,
        "counts": {
            "n_audit_rows": len(rows),
            "n_products": len(product_nodes),
            "n_explicit_observations": explicit_observation_count,
            "n_component_classes": len(component_nodes),
            "n_unique_product_component_edges": len(edges),
            "n_shared_component_classes": len(shared_components),
            "n_cross_ingredient_component_classes": len(
                cross_ingredient_components
            ),
        },
        "coverage": {
            "all_product_ids": all_product_ids,
            "observed_product_ids": observed_product_ids,
            "n_observed_products": len(observed_product_ids),
            "unresolved_product_ids": sorted(unresolved_product_ids),
            "n_unresolved_products": len(unresolved_product_ids),
        },
        "product_nodes": {
            key: product_nodes[key]
            for key in sorted(product_nodes)
        },
        "component_nodes": {
            key: component_nodes[key]
            for key in sorted(component_nodes)
        },
        "edges": edges,
        "shared_components": {
            key: shared_components[key]
            for key in sorted(
                shared_components,
                key=lambda k: (
                    -shared_components[k]["n_products"],
                    -shared_components[k]["n_active_ingredients"],
                    k,
                ),
            )
        },
        "cross_ingredient_components": {
            key: cross_ingredient_components[key]
            for key in sorted(
                cross_ingredient_components,
                key=lambda k: (
                    -cross_ingredient_components[k]["n_active_ingredients"],
                    -cross_ingredient_components[k]["n_products"],
                    k,
                ),
            )
        },
    }


def render_markdown(graph: dict[str, Any]) -> str:
    counts = graph["counts"]
    coverage = graph["coverage"]

    lines: list[str] = []

    lines.append("# Component-Level Pharmaceutical Dependency Graph v0.1")
    lines.append("")
    lines.append(
        "Generated automatically from the frozen component audit table."
    )
    lines.append("")
    lines.append(
        "**Interpretation rule:** observed component convergence is descriptive "
        "and does not by itself establish supplier identity, mandatory "
        "dependence, non-substitutability, or a common failure mode."
    )
    lines.append("")

    lines.append("## Graph summary")
    lines.append("")
    lines.append(f"- Audit rows: **{counts['n_audit_rows']}**")
    lines.append(f"- Products: **{counts['n_products']}**")
    lines.append(
        f"- Explicit component observations: "
        f"**{counts['n_explicit_observations']}**"
    )
    lines.append(
        f"- Exact physical component classes: "
        f"**{counts['n_component_classes']}**"
    )
    lines.append(
        f"- Unique product-component relationships: "
        f"**{counts['n_unique_product_component_edges']}**"
    )
    lines.append(
        f"- Shared component classes: "
        f"**{counts['n_shared_component_classes']}**"
    )
    lines.append(
        f"- Cross-ingredient component classes: "
        f"**{counts['n_cross_ingredient_component_classes']}**"
    )
    lines.append("")

    lines.append("## Coverage")
    lines.append("")
    lines.append(
        f"- Products with at least one explicit component: "
        f"**{coverage['n_observed_products']}/{counts['n_products']}**"
    )
    lines.append(
        f"- Unresolved products: "
        f"**{coverage['n_unresolved_products']}**"
    )

    if coverage["unresolved_product_ids"]:
        for product_id in coverage["unresolved_product_ids"]:
            lines.append(f"  - `{product_id}`")

    lines.append("")

    lines.append("## Cross-ingredient exact component convergence")
    lines.append("")
    lines.append(
        "| Component class | Products | Active ingredients | "
        "Ingredients | Roles |"
    )
    lines.append(
        "|---|---:|---:|---|---|"
    )

    for component_class, node in graph[
        "cross_ingredient_components"
    ].items():
        ingredients = ", ".join(node["active_ingredients"])
        roles = ", ".join(node["roles"])

        lines.append(
            f"| `{component_class}` | "
            f"{node['n_products']} | "
            f"{node['n_active_ingredients']} | "
            f"{ingredients} | "
            f"{roles} |"
        )

    if not graph["cross_ingredient_components"]:
        lines.append("| _None observed_ | 0 | 0 | | |")

    lines.append("")

    lines.append("## All exact component classes")
    lines.append("")
    lines.append(
        "| Component class | Products | Active ingredients | Roles | Parent |"
    )
    lines.append("|---|---:|---:|---|---|")

    ordered_components = sorted(
        graph["component_nodes"].items(),
        key=lambda item: (
            -item[1]["n_products"],
            -item[1]["n_active_ingredients"],
            item[0],
        ),
    )

    for component_class, node in ordered_components:
        roles = ", ".join(node["roles"])
        parents = ", ".join(node["parent_component_classes"])

        lines.append(
            f"| `{component_class}` | "
            f"{node['n_products']} | "
            f"{node['n_active_ingredients']} | "
            f"{roles} | "
            f"{parents} |"
        )

    lines.append("")

    lines.append("## Methodological note")
    lines.append("")
    lines.append(
        "Component identity is defined by the normalized physical "
        "`component_class`. Product-specific roles such as "
        "`primary_container` and `solvent_container` are retained on the "
        "relationship rather than used to create separate physical "
        "component identities."
    )
    lines.append("")
    lines.append(
        "This prevents the same physical component class from being "
        "artificially split merely because it serves different roles in "
        "different authorised product presentations."
    )
    lines.append("")
    lines.append(
        "Parent-component information is retained but is not collapsed in "
        "this exact-resolution analysis. Parent-level convergence will be "
        "evaluated separately in the multiresolution sensitivity analysis."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def write_json(graph: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(
            graph,
            handle,
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
        )
        handle.write("\n")


def write_markdown(graph: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(graph), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build an exact-resolution pharmaceutical "
            "product-component dependency graph."
        )
    )

    parser.add_argument(
        "component_audit",
        help="Path to component_audit_v0_1.csv",
    )

    parser.add_argument(
        "--json-out",
        default=None,
        help="Optional JSON output path.",
    )

    parser.add_argument(
        "--md-out",
        default=None,
        help="Optional Markdown summary output path.",
    )

    args = parser.parse_args()

    rows = read_component_audit(args.component_audit)
    graph = build_component_graph(rows)

    if args.json_out:
        write_json(graph, args.json_out)

    if args.md_out:
        write_markdown(graph, args.md_out)

    print("COMPONENT GRAPH BUILT")
    print("audit rows =", graph["counts"]["n_audit_rows"])
    print("products =", graph["counts"]["n_products"])
    print(
        "explicit observations =",
        graph["counts"]["n_explicit_observations"],
    )
    print(
        "component classes =",
        graph["counts"]["n_component_classes"],
    )
    print(
        "unique product-component edges =",
        graph["counts"]["n_unique_product_component_edges"],
    )
    print(
        "cross-ingredient components =",
        graph["counts"]["n_cross_ingredient_component_classes"],
    )
    print()

    print("CROSS-INGREDIENT COMPONENTS")

    for component_class, node in graph[
        "cross_ingredient_components"
    ].items():
        print(
            component_class,
            "=> products=",
            node["n_products"],
            "ingredients=",
            node["n_active_ingredients"],
            node["active_ingredients"],
        )


if __name__ == "__main__":
    main()