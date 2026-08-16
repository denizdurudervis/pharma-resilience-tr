from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from pharma_resilience.component_evidence_coverage import (
    read_csv,
)
from pharma_resilience.component_graph import (
    build_component_graph,
)
from pharma_resilience.component_resolution import (
    build_resolution_analysis,
)
from pharma_resilience.evidence_weighted_pair_overlap import (
    build_evidence_weighted_pair_overlap,
)


SCHEMA_VERSION = "poc_results_summary_v0_1"


def _trajectory(
    weighted: dict[str, Any],
    ingredient_a: str,
    ingredient_b: str,
) -> dict[str, Any]:
    wanted = {ingredient_a, ingredient_b}

    result: dict[str, Any] = {}

    for level_name in (
        "R0_exact",
        "R1_parent",
        "R2_terminal",
    ):
        match = None

        for pair in weighted["levels"][level_name]["pairs"]:
            if {
                pair["ingredient_a"],
                pair["ingredient_b"],
            } == wanted:
                match = pair
                break

        if match is None:
            raise ValueError(
                f"Pair not found: "
                f"{ingredient_a}, {ingredient_b}"
            )

        result[level_name] = {
            "existential_shared_component_count": (
                match[
                    "existential_shared_component_count"
                ]
            ),
            "documented_overlap_score": (
                match[
                    "documented_overlap_score"
                ]
            ),
            "componentwise_unresolved_envelope_score": (
                match[
                    "componentwise_unresolved_envelope_score"
                ]
            ),
            "envelope_increment": (
                match["envelope_increment"]
            ),
        }

    documented_values = [
        result[level]["documented_overlap_score"]
        for level in (
            "R0_exact",
            "R1_parent",
            "R2_terminal",
        )
    ]

    envelope_increments = [
        result[level]["envelope_increment"]
        for level in (
            "R0_exact",
            "R1_parent",
            "R2_terminal",
        )
    ]

    return {
        "ingredient_a": ingredient_a,
        "ingredient_b": ingredient_b,
        "levels": result,
        "documented_resolution_range": round(
            max(documented_values)
            - min(documented_values),
            6,
        ),
        "resolution_sensitive": (
            max(documented_values)
            - min(documented_values)
            > 1e-9
        ),
        "max_envelope_increment": round(
            max(envelope_increments),
            6,
        ),
        "unresolved_evidence_sensitive": (
            max(envelope_increments) > 1e-9
        ),
    }


def build_poc_results_summary(
    product_rows: list[dict[str, str]],
    component_rows: list[dict[str, str]],
) -> dict[str, Any]:

    graph = build_component_graph(
        component_rows
    )

    resolution = build_resolution_analysis(
        component_rows
    )

    weighted = build_evidence_weighted_pair_overlap(
        product_rows,
        component_rows,
    )

    ingredients = weighted["ingredients"]

    pairs: list[dict[str, Any]] = []

    for i, ingredient_a in enumerate(ingredients):
        for ingredient_b in ingredients[i + 1 :]:
            pairs.append(
                _trajectory(
                    weighted,
                    ingredient_a,
                    ingredient_b,
                )
            )

    terminal_pairs = sorted(
        pairs,
        key=lambda pair: (
            -pair["levels"]["R2_terminal"][
                "documented_overlap_score"
            ],
            pair["ingredient_a"],
            pair["ingredient_b"],
        ),
    )

    resolution_sensitive_pairs = [
        pair
        for pair in pairs
        if pair["resolution_sensitive"]
    ]

    unresolved_sensitive_pairs = [
        pair
        for pair in pairs
        if pair[
            "unresolved_evidence_sensitive"
        ]
    ]

    unresolved_insensitive_pairs = [
        pair
        for pair in pairs
        if not pair[
            "unresolved_evidence_sensitive"
        ]
    ]

    resolution_summary: dict[str, Any] = {}

    for level_name in (
        "R0_exact",
        "R1_parent",
        "R2_terminal",
    ):
        resolution_summary[level_name] = {
            "n_component_classes": (
                resolution["levels"][level_name][
                    "n_component_classes"
                ]
            ),
            "n_product_component_edges": (
                resolution["levels"][level_name][
                    "n_product_component_edges"
                ]
            ),
            "n_cross_ingredient_classes": (
                resolution["levels"][level_name][
                    "n_cross_ingredient_classes"
                ]
            ),
            "mean_documented_overlap_score": (
                weighted["levels"][level_name][
                    "mean_documented_overlap_score"
                ]
            ),
            "mean_componentwise_unresolved_envelope_score": (
                weighted["levels"][level_name][
                    "mean_componentwise_unresolved_envelope_score"
                ]
            ),
        }

    strongest_terminal_score = (
        terminal_pairs[0]["levels"]["R2_terminal"][
            "documented_overlap_score"
        ]
        if terminal_pairs
        else 0.0
    )

    strongest_terminal_pairs = [
        pair
        for pair in terminal_pairs
        if pair["levels"]["R2_terminal"][
            "documented_overlap_score"
        ]
        == strongest_terminal_score
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "dataset": {
            "n_audit_rows": graph["counts"][
                "n_audit_rows"
            ],
            "n_products": graph["counts"][
                "n_products"
            ],
            "n_explicit_component_observations": (
                graph["counts"][
                    "n_explicit_observations"
                ]
            ),
            "n_unresolved_products": (
                graph["coverage"][
                    "n_unresolved_products"
                ]
            ),
            "unresolved_product_ids": (
                graph["coverage"][
                    "unresolved_product_ids"
                ]
            ),
            "n_exact_component_classes": (
                graph["counts"][
                    "n_component_classes"
                ]
            ),
            "n_unique_product_component_edges": (
                graph["counts"][
                    "n_unique_product_component_edges"
                ]
            ),
        },
        "ingredients": ingredients,
        "resolution_summary": (
            resolution_summary
        ),
        "pair_trajectories": pairs,
        "classification": {
            "n_pairs": len(pairs),
            "n_resolution_sensitive_pairs": len(
                resolution_sensitive_pairs
            ),
            "resolution_sensitive_pairs": [
                [
                    pair["ingredient_a"],
                    pair["ingredient_b"],
                ]
                for pair in resolution_sensitive_pairs
            ],
            "n_unresolved_evidence_sensitive_pairs": len(
                unresolved_sensitive_pairs
            ),
            "unresolved_evidence_sensitive_pairs": [
                [
                    pair["ingredient_a"],
                    pair["ingredient_b"],
                ]
                for pair in unresolved_sensitive_pairs
            ],
            "n_unresolved_evidence_insensitive_pairs": len(
                unresolved_insensitive_pairs
            ),
            "unresolved_evidence_insensitive_pairs": [
                [
                    pair["ingredient_a"],
                    pair["ingredient_b"],
                ]
                for pair in unresolved_insensitive_pairs
            ],
        },
        "strongest_terminal_documented_overlap": {
            "score": strongest_terminal_score,
            "pairs": [
                [
                    pair["ingredient_a"],
                    pair["ingredient_b"],
                ]
                for pair in strongest_terminal_pairs
            ],
        },
        "interpretation": {
            "resolution_sensitive": (
                "Documented overlap changes across "
                "R0, R1 and R2."
            ),
            "unresolved_evidence_sensitive": (
                "At least one resolution level has a "
                "positive componentwise unresolved "
                "sensitivity-envelope increment."
            ),
            "warning": (
                "Unresolved-evidence sensitivity is not "
                "physical supply-chain fragility. The "
                "componentwise envelope is not a jointly "
                "feasible physical upper bound."
            ),
        },
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:
    dataset = summary["dataset"]

    lines: list[str] = []

    lines.append(
        "# Pharmaceutical Component-Resilience "
        "PoC Results Summary v0.1"
    )
    lines.append("")

    lines.append("## Frozen dataset")
    lines.append("")
    lines.append(
        f"- Products: **{dataset['n_products']}**"
    )
    lines.append(
        f"- Component-audit rows: "
        f"**{dataset['n_audit_rows']}**"
    )
    lines.append(
        f"- Explicit component observations: "
        f"**{dataset['n_explicit_component_observations']}**"
    )
    lines.append(
        f"- Unresolved products: "
        f"**{dataset['n_unresolved_products']}**"
    )

    if dataset["unresolved_product_ids"]:
        lines.append(
            "- Unresolved product IDs: "
            + ", ".join(
                f"`{item}`"
                for item in dataset[
                    "unresolved_product_ids"
                ]
            )
        )

    lines.append("")

    lines.append("## Resolution trajectory")
    lines.append("")
    lines.append(
        "| Level | Component classes | "
        "Cross-ingredient classes | "
        "Mean documented pair overlap | "
        "Mean unresolved envelope |"
    )
    lines.append(
        "|---|---:|---:|---:|---:|"
    )

    for level_name, result in summary[
        "resolution_summary"
    ].items():
        lines.append(
            f"| `{level_name}` | "
            f"{result['n_component_classes']} | "
            f"{result['n_cross_ingredient_classes']} | "
            f"{result['mean_documented_overlap_score']:.3f} | "
            f"{result['mean_componentwise_unresolved_envelope_score']:.3f} |"
        )

    lines.append("")

    lines.append("## Ingredient-pair trajectories")
    lines.append("")
    lines.append(
        "| Pair | R0 documented | R1 documented | "
        "R2 documented | Resolution-sensitive | "
        "Unresolved-evidence-sensitive |"
    )
    lines.append(
        "|---|---:|---:|---:|---|---|"
    )

    for pair in sorted(
        summary["pair_trajectories"],
        key=lambda item: (
            -item["levels"]["R2_terminal"][
                "documented_overlap_score"
            ],
            item["ingredient_a"],
            item["ingredient_b"],
        ),
    ):
        lines.append(
            f"| {pair['ingredient_a']} – "
            f"{pair['ingredient_b']} | "
            f"{pair['levels']['R0_exact']['documented_overlap_score']:.3f} | "
            f"{pair['levels']['R1_parent']['documented_overlap_score']:.3f} | "
            f"{pair['levels']['R2_terminal']['documented_overlap_score']:.3f} | "
            f"{'Yes' if pair['resolution_sensitive'] else 'No'} | "
            f"{'Yes' if pair['unresolved_evidence_sensitive'] else 'No'} |"
        )

    lines.append("")

    lines.append("## PoC findings")
    lines.append("")

    strongest = summary[
        "strongest_terminal_documented_overlap"
    ]

    strongest_names = "; ".join(
        " – ".join(pair)
        for pair in strongest["pairs"]
    )

    lines.append(
        f"- Highest terminal documented-overlap score: "
        f"**{strongest['score']:.3f}**, observed for "
        f"**{strongest_names}**."
    )

    lines.append(
        f"- Resolution-sensitive ingredient pairs: "
        f"**{summary['classification']['n_resolution_sensitive_pairs']}"
        f"/{summary['classification']['n_pairs']}**."
    )

    lines.append(
        f"- Pairs sensitive to fully unresolved-product "
        f"evidence: "
        f"**{summary['classification']['n_unresolved_evidence_sensitive_pairs']}"
        f"/{summary['classification']['n_pairs']}**."
    )

    lines.append("")

    lines.append("## Interpretation limits")
    lines.append("")
    lines.append(
        "Observed or evidence-weighted component overlap "
        "does not establish supplier identity, mandatory "
        "dependence, non-substitutability, common failure "
        "mode, disruption probability, or national shortage "
        "risk."
    )
    lines.append("")
    lines.append(
        "The current frozen sample is a proof of concept "
        "within a parenteral acid-suppression product family. "
        "The observed convergence may therefore partly reflect "
        "dosage-form conditioning and must be tested in a "
        "pre-specified expanded sample with diversified "
        "negative controls."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "product_audit"
    )

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

    product_rows = read_csv(
        args.product_audit
    )

    component_rows = read_csv(
        args.component_audit
    )

    summary = build_poc_results_summary(
        product_rows,
        component_rows,
    )

    if args.json_out:
        path = Path(args.json_out)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                summary,
                handle,
                ensure_ascii=False,
                indent=2,
            )
            handle.write("\n")

    if args.md_out:
        path = Path(args.md_out)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            render_markdown(summary),
            encoding="utf-8",
        )

    print("POC RESULTS SUMMARY")
    print()

    print("DATASET")
    for key, value in summary[
        "dataset"
    ].items():
        print(" ", key, "=", value)

    print()
    print("RESOLUTION SUMMARY")

    for level, values in summary[
        "resolution_summary"
    ].items():
        print(
            level,
            "classes=",
            values["n_component_classes"],
            "cross-ingredient=",
            values["n_cross_ingredient_classes"],
            "mean documented=",
            values["mean_documented_overlap_score"],
            "mean envelope=",
            values[
                "mean_componentwise_unresolved_envelope_score"
            ],
        )

    print()
    print("PAIR CLASSIFICATION")
    print(
        " resolution-sensitive =",
        summary["classification"][
            "resolution_sensitive_pairs"
        ],
    )
    print(
        " unresolved-evidence-sensitive =",
        summary["classification"][
            "unresolved_evidence_sensitive_pairs"
        ],
    )
    print(
        " unresolved-evidence-insensitive =",
        summary["classification"][
            "unresolved_evidence_insensitive_pairs"
        ],
    )

    print()
    print(
        "STRONGEST TERMINAL DOCUMENTED OVERLAP =",
        summary[
            "strongest_terminal_documented_overlap"
        ],
    )


if __name__ == "__main__":
    main()