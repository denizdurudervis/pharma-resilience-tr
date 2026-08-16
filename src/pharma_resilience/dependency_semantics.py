from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


SEMANTICS = {
    "process": {
        "representation_kind": "descriptive_process_class",
        "single_failure_entity": False,
        "mandatory_product_dependency_established": False,
        "resolution_needed": (
            "A process class is not a unique physical "
            "failure entity."
        ),
    },

    "container": {
        "representation_kind": "physical_component_class",
        "single_failure_entity": False,
        "mandatory_product_dependency_established": False,
        "resolution_needed": (
            "Supplier, origin, facility, or component-specific "
            "resolution is required before direct interdiction."
        ),
    },

    "closure": {
        "representation_kind": "physical_component_class",
        "single_failure_entity": False,
        "mandatory_product_dependency_established": False,
        "resolution_needed": (
            "Supplier, origin, facility, or component-specific "
            "resolution is required before direct interdiction."
        ),
    },

    "site": {
        "representation_kind": "observed_site_mention",
        "single_failure_entity": False,
        "mandatory_product_dependency_established": False,
        "resolution_needed": (
            "The public document contains a named site mention, "
            "but entity normalization is required before treating "
            "it as a unique physical facility. Public evidence also "
            "does not establish site role, mandatory dependence, "
            "or exhaustiveness of the approved site list."
        ),
    },
}


def classify_dependency_node(
    node: dict[str, Any],
) -> dict[str, Any]:
    dependency_type = node.get(
        "dependency_type",
        "",
    )

    semantics = SEMANTICS.get(
        dependency_type,
        {
            "representation_kind": "unclassified",
            "single_failure_entity": False,
            "mandatory_product_dependency_established": False,
            "resolution_needed": (
                "Dependency type requires explicit semantic "
                "classification before disruption modeling."
            ),
        },
    )

    annotated = dict(node)
    annotated.update(semantics)

    annotated["direct_interdiction_ready"] = bool(
        annotated["single_failure_entity"]
        and annotated[
            "mandatory_product_dependency_established"
        ]
    )

    return annotated


def annotate_dependency_graph(
    graph: dict[str, Any],
) -> dict[str, Any]:
    annotated_nodes = {
        node_id: classify_dependency_node(node)
        for node_id, node
        in graph["dependency_nodes"].items()
    }

    representation_counts = Counter(
        node["representation_kind"]
        for node in annotated_nodes.values()
    )

    single_failure_entities = sorted(
        node_id
        for node_id, node
        in annotated_nodes.items()
        if node["single_failure_entity"]
    )

    mandatory_dependencies = sorted(
        node_id
        for node_id, node
        in annotated_nodes.items()
        if node[
            "mandatory_product_dependency_established"
        ]
    )

    direct_interdiction_ready = sorted(
        node_id
        for node_id, node
        in annotated_nodes.items()
        if node["direct_interdiction_ready"]
    )

    return {
        "n_dependency_nodes": len(
            annotated_nodes
        ),

        "representation_counts": dict(
            sorted(
                representation_counts.items()
            )
        ),

        "n_single_failure_entities": len(
            single_failure_entities
        ),

        "single_failure_entities": (
            single_failure_entities
        ),

        "n_mandatory_dependencies_established": len(
            mandatory_dependencies
        ),

        "mandatory_dependencies_established": (
            mandatory_dependencies
        ),

        "n_direct_interdiction_ready": len(
            direct_interdiction_ready
        ),

        "direct_interdiction_ready": (
            direct_interdiction_ready
        ),

        "dependency_nodes": annotated_nodes,

        "interpretation": (
            "A shared dependency node is not automatically "
            "a shared failure mode. Raw site mentions require "
            "entity normalization before they can be treated as "
            "unique physical facilities. Direct interdiction is "
            "permitted only when a node is a resolved single "
            "physical failure entity and mandatory product "
            "dependence on that entity is established."
        ),
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Dependency Semantics v0.1"
    )
    lines.append("")

    lines.append(
        "Semantic gate between the observed dependency "
        "graph and disruption/interdiction modeling."
    )
    lines.append("")

    lines.append(
        "> Shared node does not imply shared failure mode."
    )
    lines.append("")

    lines.append("## Representation classes")
    lines.append("")

    for kind, count in summary[
        "representation_counts"
    ].items():
        lines.append(
            f"- `{kind}`: **{count}**"
        )

    lines.append("")
    lines.append("## Interdiction readiness")
    lines.append("")

    lines.append(
        f"- Dependency nodes: "
        f"**{summary['n_dependency_nodes']}**"
    )

    lines.append(
        f"- Resolved single physical failure entities: "
        f"**{summary['n_single_failure_entities']}**"
    )

    lines.append(
        "- Product-mandatory dependencies established: "
        f"**{summary['n_mandatory_dependencies_established']}**"
    )

    lines.append(
        "- Direct-interdiction-ready nodes: "
        f"**{summary['n_direct_interdiction_ready']}**"
    )

    lines.append("")
    lines.append("## Current modeling rule")
    lines.append("")

    lines.append(
        "Process classes, container classes, and closure "
        "classes must not be interpreted as unique physical "
        "failure entities."
    )
    lines.append("")

    lines.append(
        "Named manufacturing-site strings are currently "
        "treated only as observed site mentions. Entity "
        "normalization is required before determining whether "
        "two mentions correspond to the same physical facility."
    )
    lines.append("")

    lines.append(
        "Even after site entity resolution, current public "
        "evidence does not establish site role, mandatory "
        "dependence, or exhaustiveness of the approved "
        "manufacturing-site set."
    )
    lines.append("")

    lines.append(
        "Therefore no current dependency node is assumed "
        "to disable a product deterministically when removed."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Annotate dependency graph nodes with "
            "failure-model semantics."
        )
    )

    parser.add_argument("graph_json")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")

    args = parser.parse_args()

    with open(
        args.graph_json,
        encoding="utf-8",
    ) as handle:
        graph = json.load(handle)

    summary = annotate_dependency_graph(
        graph
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