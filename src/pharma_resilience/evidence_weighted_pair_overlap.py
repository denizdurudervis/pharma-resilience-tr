from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from pharma_resilience.component_evidence_coverage import (
    build_component_evidence_coverage,
    read_csv,
)
from pharma_resilience.ingredient_pair_convergence import (
    build_pair_convergence,
    pair_id,
)


SCHEMA_VERSION = "evidence_weighted_pair_overlap_v0_1"


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def build_evidence_weighted_pair_overlap(
    product_rows: list[dict[str, str]],
    component_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """
    Combine existential ingredient-pair convergence with documentary
    component coverage.

    documented_overlap_score
    ------------------------
    For ingredients a and b at resolution r:

        sum_c min(d_ac, d_bc)

    where d_ac is the fraction of all frozen-sample products for
    ingredient a with explicit documentary support for component c.

    componentwise_unresolved_envelope_score
    ----------------------------------------
    The same calculation using the unresolved-only componentwise
    sensitivity scenario.

    IMPORTANT:
    The componentwise envelope is NOT a jointly feasible physical upper
    bound. A fully unresolved product can contribute to several component
    classes independently in this sensitivity calculation, including
    classes that could be mutually exclusive in a single real product.
    """

    coverage = build_component_evidence_coverage(
        product_rows,
        component_rows,
    )

    existential = build_pair_convergence(
        component_rows
    )

    ingredients = coverage["ingredients"]

    levels: dict[str, Any] = {}

    for level_name in (
        "R0_exact",
        "R1_parent",
        "R2_terminal",
    ):
        component_nodes = coverage[
            "levels"
        ][level_name]["components"]

        existential_lookup = {
            pair["pair_id"]: pair
            for pair in existential[
                "levels"
            ][level_name]["pairs"]
        }

        pair_results: list[dict[str, Any]] = []

        for ingredient_a, ingredient_b in combinations(
            ingredients,
            2,
        ):
            pid = pair_id(
                ingredient_a,
                ingredient_b,
            )

            documented_score = 0.0
            envelope_score = 0.0

            contributions: list[dict[str, Any]] = []

            for component_class in sorted(
                component_nodes
            ):
                ingredient_values = component_nodes[
                    component_class
                ]["ingredients"]

                values_a = ingredient_values[
                    ingredient_a
                ]
                values_b = ingredient_values[
                    ingredient_b
                ]

                documented_a = _safe_float(
                    values_a[
                        "documented_share_frozen"
                    ]
                )
                documented_b = _safe_float(
                    values_b[
                        "documented_share_frozen"
                    ]
                )

                envelope_a = _safe_float(
                    values_a[
                        "unresolved_only_upper_scenario"
                    ]
                )
                envelope_b = _safe_float(
                    values_b[
                        "unresolved_only_upper_scenario"
                    ]
                )

                documented_contribution = min(
                    documented_a,
                    documented_b,
                )

                envelope_contribution = min(
                    envelope_a,
                    envelope_b,
                )

                documented_score += (
                    documented_contribution
                )

                envelope_score += (
                    envelope_contribution
                )

                if (
                    documented_contribution > 0
                    or envelope_contribution > 0
                ):
                    contributions.append(
                        {
                            "component_class": (
                                component_class
                            ),
                            "ingredient_a_documented_share": round(
                                documented_a,
                                6,
                            ),
                            "ingredient_b_documented_share": round(
                                documented_b,
                                6,
                            ),
                            "documented_overlap_contribution": round(
                                documented_contribution,
                                6,
                            ),
                            "ingredient_a_componentwise_envelope_share": round(
                                envelope_a,
                                6,
                            ),
                            "ingredient_b_componentwise_envelope_share": round(
                                envelope_b,
                                6,
                            ),
                            "componentwise_envelope_contribution": round(
                                envelope_contribution,
                                6,
                            ),
                        }
                    )

            existential_pair = existential_lookup[
                pid
            ]

            pair_results.append(
                {
                    "pair_id": pid,
                    "ingredient_a": ingredient_a,
                    "ingredient_b": ingredient_b,
                    "existential_shared_component_count": (
                        existential_pair[
                            "n_shared_components"
                        ]
                    ),
                    "existential_shared_component_classes": (
                        existential_pair[
                            "shared_component_classes"
                        ]
                    ),
                    "documented_overlap_score": round(
                        documented_score,
                        6,
                    ),
                    "componentwise_unresolved_envelope_score": round(
                        envelope_score,
                        6,
                    ),
                    "envelope_increment": round(
                        envelope_score
                        - documented_score,
                        6,
                    ),
                    "component_contributions": (
                        contributions
                    ),
                }
            )

        pair_results.sort(
            key=lambda item: (
                -item[
                    "documented_overlap_score"
                ],
                -item[
                    "componentwise_unresolved_envelope_score"
                ],
                item["ingredient_a"],
                item["ingredient_b"],
            )
        )

        documented_scores = [
            pair[
                "documented_overlap_score"
            ]
            for pair in pair_results
        ]

        envelope_scores = [
            pair[
                "componentwise_unresolved_envelope_score"
            ]
            for pair in pair_results
        ]

        levels[level_name] = {
            "n_pairs": len(pair_results),
            "mean_documented_overlap_score": round(
                sum(documented_scores)
                / len(documented_scores),
                6,
            )
            if documented_scores
            else 0.0,
            "mean_componentwise_unresolved_envelope_score": round(
                sum(envelope_scores)
                / len(envelope_scores),
                6,
            )
            if envelope_scores
            else 0.0,
            "max_documented_overlap_score": (
                max(documented_scores)
                if documented_scores
                else 0.0
            ),
            "max_componentwise_unresolved_envelope_score": (
                max(envelope_scores)
                if envelope_scores
                else 0.0
            ),
            "pairs": pair_results,
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "ingredients": ingredients,
        "levels": levels,
        "interpretation": {
            "documented_overlap_score": (
                "Sum across component classes of the minimum "
                "frozen-sample documentary support share for "
                "the two active ingredients."
            ),
            "componentwise_unresolved_envelope_score": (
                "Sensitivity score obtained after allowing every "
                "fully unresolved product to support each component "
                "class independently."
            ),
            "critical_warning": (
                "The componentwise unresolved envelope is not a "
                "jointly feasible physical upper bound and is not "
                "a probability. The same unresolved product may "
                "contribute independently to mutually exclusive "
                "component classes."
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
        "# Evidence-Weighted Ingredient-Pair "
        "Component Overlap v0.1"
    )
    lines.append("")

    lines.append(
        "Observed component convergence weighted by "
        "frozen-sample documentary support."
    )
    lines.append("")

    lines.append(
        "**Critical interpretation rule:** the "
        "`componentwise_unresolved_envelope_score` is a "
        "sensitivity envelope, not a jointly feasible physical "
        "upper bound and not a probability."
    )
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(
        "| Level | Pairs | Mean documented overlap | "
        "Mean unresolved envelope | Maximum documented |"
    )
    lines.append("|---|---:|---:|---:|---:|")

    for level_name, result in analysis[
        "levels"
    ].items():
        lines.append(
            f"| `{level_name}` | "
            f"{result['n_pairs']} | "
            f"{result['mean_documented_overlap_score']:.3f} | "
            f"{result['mean_componentwise_unresolved_envelope_score']:.3f} | "
            f"{result['max_documented_overlap_score']:.3f} |"
        )

    lines.append("")

    for level_name, result in analysis[
        "levels"
    ].items():
        lines.append(
            f"## {level_name}"
        )
        lines.append("")

        lines.append(
            "| Ingredient pair | Existential classes | "
            "Documented overlap | Unresolved envelope | "
            "Envelope increment |"
        )
        lines.append(
            "|---|---:|---:|---:|---:|"
        )

        for pair in result["pairs"]:
            lines.append(
                f"| {pair['ingredient_a']} – "
                f"{pair['ingredient_b']} | "
                f"{pair['existential_shared_component_count']} | "
                f"{pair['documented_overlap_score']:.3f} | "
                f"{pair['componentwise_unresolved_envelope_score']:.3f} | "
                f"{pair['envelope_increment']:.3f} |"
            )

        lines.append("")

    lines.append("## Interpretation")
    lines.append("")

    lines.append(
        "The existential count answers whether a component "
        "class appears anywhere in both active-ingredient "
        "product portfolios."
    )
    lines.append("")

    lines.append(
        "The documented overlap score additionally reflects "
        "how many frozen-sample products have explicit "
        "documentary support for those component classes."
    )
    lines.append("")

    lines.append(
        "The unresolved envelope shows sensitivity to products "
        "without any explicit component evidence. It must not "
        "be interpreted as a physically achievable simultaneous "
        "configuration."
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

    analysis = (
        build_evidence_weighted_pair_overlap(
            product_rows,
            component_rows,
        )
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

    print(
        "EVIDENCE-WEIGHTED PAIR OVERLAP"
    )
    print()

    for level_name, result in analysis[
        "levels"
    ].items():
        print(level_name)

        print(
            "  mean documented overlap =",
            result[
                "mean_documented_overlap_score"
            ],
        )

        print(
            "  mean unresolved envelope =",
            result[
                "mean_componentwise_unresolved_envelope_score"
            ],
        )

        for pair in result["pairs"]:
            print(
                " ",
                pair["ingredient_a"],
                "<->",
                pair["ingredient_b"],
                "existential=",
                pair[
                    "existential_shared_component_count"
                ],
                "documented=",
                pair[
                    "documented_overlap_score"
                ],
                "envelope=",
                pair[
                    "componentwise_unresolved_envelope_score"
                ],
                "increment=",
                pair[
                    "envelope_increment"
                ],
            )

        print()


if __name__ == "__main__":
    main()