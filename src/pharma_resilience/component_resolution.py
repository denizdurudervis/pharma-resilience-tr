from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "component_resolution_v0_1"


def read_component_audit(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def build_parent_map(
    rows: list[dict[str, str]],
) -> dict[str, str]:
    """
    Build the observed component-class parent mapping.

    Self-parent observations are treated as terminal/no-op mappings.
    Conflicting non-empty parents for the same component class are rejected.
    """

    observed: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        status = (
            row.get("observation_status") or ""
        ).strip().lower()

        child = (
            row.get("component_class") or ""
        ).strip()

        parent = (
            row.get("parent_component_class") or ""
        ).strip()

        if status != "explicit":
            continue

        if not child or not parent:
            continue

        observed[child].add(parent)

    parent_map: dict[str, str] = {}

    for child, parents in sorted(observed.items()):
        non_self = {
            parent
            for parent in parents
            if parent != child
        }

        if len(non_self) > 1:
            raise ValueError(
                f"Conflicting parents for {child}: "
                f"{sorted(non_self)}"
            )

        if non_self:
            parent_map[child] = next(iter(non_self))
        else:
            # Self-parent only: terminal/no-op.
            parent_map[child] = child

    return parent_map


def one_parent_step(
    component_class: str,
    parent_map: dict[str, str],
) -> str:
    parent = parent_map.get(
        component_class,
        component_class,
    )

    if parent == component_class:
        return component_class

    return parent


def terminal_parent(
    component_class: str,
    parent_map: dict[str, str],
) -> str:
    """
    Follow observed parent links until a terminal class is reached.

    Self-parent links terminate traversal.
    Cycles involving more than one distinct class raise an error.
    """

    current = component_class
    visited: list[str] = []

    while True:
        parent = parent_map.get(current)

        if not parent or parent == current:
            return current

        if parent in visited:
            cycle = visited + [current, parent]
            raise ValueError(
                "Parent hierarchy cycle detected: "
                + " -> ".join(cycle)
            )

        visited.append(current)
        current = parent


def resolution_label(
    exact_class: str,
    level: str,
    parent_map: dict[str, str],
) -> str:
    if level == "R0_exact":
        return exact_class

    if level == "R1_parent":
        return one_parent_step(
            exact_class,
            parent_map,
        )

    if level == "R2_terminal":
        return terminal_parent(
            exact_class,
            parent_map,
        )

    raise ValueError(
        f"Unknown resolution level: {level}"
    )


def aggregate_resolution(
    rows: list[dict[str, str]],
    level: str,
    parent_map: dict[str, str],
) -> dict[str, Any]:
    """
    Aggregate explicit product-component observations at one resolution.

    Product-component identity is role-agnostic. Roles remain attributes
    of the relationship.
    """

    node_acc: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "product_ids": set(),
            "active_ingredients": set(),
            "exact_component_classes": set(),
            "roles": set(),
        }
    )

    edge_acc: dict[
        tuple[str, str],
        dict[str, Any],
    ] = defaultdict(
        lambda: {
            "roles": set(),
            "exact_component_classes": set(),
        }
    )

    for row in rows:
        status = (
            row.get("observation_status") or ""
        ).strip().lower()

        exact_class = (
            row.get("component_class") or ""
        ).strip()

        if status != "explicit" or not exact_class:
            continue

        product_id = (
            row.get("product_id") or ""
        ).strip()

        active_ingredient = (
            row.get("active_ingredient") or ""
        ).strip()

        role = (
            row.get("component_role") or ""
        ).strip()

        resolved_class = resolution_label(
            exact_class,
            level,
            parent_map,
        )

        node = node_acc[resolved_class]
        node["product_ids"].add(product_id)

        if active_ingredient:
            node["active_ingredients"].add(
                active_ingredient
            )

        node["exact_component_classes"].add(
            exact_class
        )

        if role:
            node["roles"].add(role)

        edge = edge_acc[
            (product_id, resolved_class)
        ]

        edge["exact_component_classes"].add(
            exact_class
        )

        if role:
            edge["roles"].add(role)

    nodes: dict[str, dict[str, Any]] = {}

    for component_class, values in node_acc.items():
        product_ids = sorted(
            values["product_ids"]
        )

        ingredients = sorted(
            values["active_ingredients"]
        )

        nodes[component_class] = {
            "component_class": component_class,
            "n_products": len(product_ids),
            "product_ids": product_ids,
            "n_active_ingredients": len(
                ingredients
            ),
            "active_ingredients": ingredients,
            "n_exact_classes_collapsed": len(
                values[
                    "exact_component_classes"
                ]
            ),
            "exact_component_classes": sorted(
                values[
                    "exact_component_classes"
                ]
            ),
            "roles": sorted(values["roles"]),
        }

    edges: list[dict[str, Any]] = []

    for (
        product_id,
        component_class,
    ), values in sorted(edge_acc.items()):
        edges.append(
            {
                "product_id": product_id,
                "component_class": (
                    component_class
                ),
                "roles": sorted(
                    values["roles"]
                ),
                "exact_component_classes": (
                    sorted(
                        values[
                            "exact_component_classes"
                        ]
                    )
                ),
            }
        )

    cross_ingredient = {
        key: value
        for key, value in nodes.items()
        if value[
            "n_active_ingredients"
        ] >= 2
    }

    return {
        "level": level,
        "n_component_classes": len(nodes),
        "n_product_component_edges": len(
            edges
        ),
        "n_cross_ingredient_classes": len(
            cross_ingredient
        ),
        "component_nodes": {
            key: nodes[key]
            for key in sorted(nodes)
        },
        "edges": edges,
        "cross_ingredient_components": {
            key: cross_ingredient[key]
            for key in sorted(
                cross_ingredient,
                key=lambda k: (
                    -cross_ingredient[k][
                        "n_active_ingredients"
                    ],
                    -cross_ingredient[k][
                        "n_products"
                    ],
                    k,
                ),
            )
        },
    }


def build_resolution_analysis(
    rows: list[dict[str, str]],
) -> dict[str, Any]:
    parent_map = build_parent_map(rows)

    levels = {}

    for level in (
        "R0_exact",
        "R1_parent",
        "R2_terminal",
    ):
        levels[level] = aggregate_resolution(
            rows,
            level,
            parent_map,
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "parent_map": {
            key: parent_map[key]
            for key in sorted(parent_map)
        },
        "levels": levels,
    }


def render_markdown(
    analysis: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Pharmaceutical Component "
        "Resolution Sensitivity v0.1"
    )
    lines.append("")
    lines.append(
        "Observed product-component "
        "convergence evaluated at "
        "increasingly coarse physical "
        "component resolution."
    )
    lines.append("")
    lines.append(
        "**Important:** aggregation "
        "changes descriptive component "
        "identity only. It does not "
        "establish supplier identity, "
        "mandatory dependence, "
        "non-substitutability, or a "
        "common failure mode."
    )
    lines.append("")

    lines.append("## Resolution definitions")
    lines.append("")
    lines.append(
        "- `R0_exact`: exact normalized "
        "component class."
    )
    lines.append(
        "- `R1_parent`: one observed "
        "parent step."
    )
    lines.append(
        "- `R2_terminal`: transitive "
        "observed parent family."
    )
    lines.append("")

    lines.append("## Resolution summary")
    lines.append("")
    lines.append(
        "| Level | Component classes | "
        "Product-component edges | "
        "Cross-ingredient classes |"
    )
    lines.append("|---|---:|---:|---:|")

    for level, result in analysis[
        "levels"
    ].items():
        lines.append(
            f"| `{level}` | "
            f"{result['n_component_classes']} | "
            f"{result['n_product_component_edges']} | "
            f"{result['n_cross_ingredient_classes']} |"
        )

    lines.append("")

    for level, result in analysis[
        "levels"
    ].items():
        lines.append(f"## {level}")
        lines.append("")
        lines.append(
            "| Component class | Products | "
            "Active ingredients | "
            "Exact classes collapsed |"
        )
        lines.append("|---|---:|---:|---:|")

        ordered = sorted(
            result[
                "component_nodes"
            ].items(),
            key=lambda item: (
                -item[1][
                    "n_active_ingredients"
                ],
                -item[1]["n_products"],
                item[0],
            ),
        )

        for name, node in ordered:
            lines.append(
                f"| `{name}` | "
                f"{node['n_products']} | "
                f"{node['n_active_ingredients']} | "
                f"{node['n_exact_classes_collapsed']} |"
            )

        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "If observed convergence increases "
        "as resolution becomes coarser, "
        "the apparent redundancy structure "
        "is resolution-dependent."
    )
    lines.append("")
    lines.append(
        "Conversely, convergence that "
        "persists at exact resolution is "
        "supported without requiring "
        "parent-family aggregation."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "component_audit"
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

    analysis = build_resolution_analysis(
        rows
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

    print("COMPONENT RESOLUTION ANALYSIS")
    print()

    for level, result in analysis[
        "levels"
    ].items():
        print(level)
        print(
            "  component classes =",
            result[
                "n_component_classes"
            ],
        )
        print(
            "  product-component edges =",
            result[
                "n_product_component_edges"
            ],
        )
        print(
            "  cross-ingredient classes =",
            result[
                "n_cross_ingredient_classes"
            ],
        )

        for name, node in result[
            "cross_ingredient_components"
        ].items():
            print(
                " ",
                name,
                "=> products=",
                node["n_products"],
                "ingredients=",
                node[
                    "n_active_ingredients"
                ],
                node[
                    "active_ingredients"
                ],
            )

        print()


if __name__ == "__main__":
    main()