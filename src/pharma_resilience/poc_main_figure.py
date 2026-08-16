from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


LEVELS = [
    "R0_exact",
    "R1_parent",
    "R2_terminal",
]

LEVEL_LABELS = [
    "R0\nExact",
    "R1\nParent",
    "R2\nTerminal",
]


def load_summary(path: str | Path) -> dict:
    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def build_plot_payload(
    summary: dict,
) -> dict:
    mean_documented = [
        summary["resolution_summary"][level][
            "mean_documented_overlap_score"
        ]
        for level in LEVELS
    ]

    mean_envelope = [
        summary["resolution_summary"][level][
            "mean_componentwise_unresolved_envelope_score"
        ]
        for level in LEVELS
    ]

    pair_series = []

    for pair in summary["pair_trajectories"]:
        pair_series.append(
            {
                "label": (
                    f"{pair['ingredient_a']} – "
                    f"{pair['ingredient_b']}"
                ),
                "values": [
                    pair["levels"][level][
                        "documented_overlap_score"
                    ]
                    for level in LEVELS
                ],
                "resolution_sensitive": (
                    pair["resolution_sensitive"]
                ),
                "unresolved_evidence_sensitive": (
                    pair[
                        "unresolved_evidence_sensitive"
                    ]
                ),
            }
        )

    pair_series.sort(
        key=lambda item: (
            -item["values"][-1],
            item["label"],
        )
    )

    return {
        "mean_documented": mean_documented,
        "mean_envelope": mean_envelope,
        "pair_series": pair_series,
    }


def make_figure(
    summary: dict,
    output_path: str | Path,
) -> None:
    payload = build_plot_payload(summary)

    fig = plt.figure(
        figsize=(12, 10),
        constrained_layout=True,
    )

    grid = fig.add_gridspec(
        2,
        1,
        height_ratios=[1, 1.45],
    )

    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[1, 0])

    x = list(range(len(LEVELS)))

    # ============================================================
    # PANEL A
    # ============================================================

    ax1.plot(
        x,
        payload["mean_documented"],
        marker="o",
        linewidth=2.2,
        label="Mean documented overlap",
    )

    ax1.plot(
        x,
        payload["mean_envelope"],
        marker="s",
        linestyle="--",
        linewidth=1.8,
        label="Mean unresolved sensitivity envelope",
    )

    for i, value in enumerate(
        payload["mean_documented"]
    ):
        ax1.annotate(
            f"{value:.3f}",
            (x[i], value),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )

    for i, value in enumerate(
        payload["mean_envelope"]
    ):
        ax1.annotate(
            f"{value:.3f}",
            (x[i], value),
            xytext=(0, -16),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )

    ax1.set_xticks(
        x,
        LEVEL_LABELS,
    )

    ax1.set_ylabel(
        "Mean pairwise component overlap"
    )

    ax1.set_title(
        "A. Resolution dependence of evidence-supported "
        "component convergence",
        loc="left",
        fontweight="bold",
    )

    ax1.legend(
        frameon=True,
    )

    ax1.text(
        0.99,
        0.04,
        "Envelope = componentwise unresolved-product "
        "sensitivity scenario;\n"
        "not a jointly feasible physical upper bound.",
        transform=ax1.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
    )

    # ============================================================
    # PANEL B — HEATMAP
    # ============================================================

    pair_series = payload["pair_series"]

    matrix = np.array(
        [
            item["values"]
            for item in pair_series
        ],
        dtype=float,
    )

    image = ax2.imshow(
        matrix,
        aspect="auto",
    )

    ax2.set_xticks(
        np.arange(len(LEVELS)),
        LEVEL_LABELS,
    )

    ylabels = []

    for item in pair_series:
        suffix = ""

        if item["resolution_sensitive"]:
            suffix += " *"

        if item["unresolved_evidence_sensitive"]:
            suffix += " †"

        ylabels.append(
            item["label"] + suffix
        )

    ax2.set_yticks(
        np.arange(len(pair_series)),
        ylabels,
    )

    for row_index in range(
        matrix.shape[0]
    ):
        for col_index in range(
            matrix.shape[1]
        ):
            value = matrix[
                row_index,
                col_index,
            ]

            ax2.text(
                col_index,
                row_index,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=10,
            )

    ax2.set_title(
        "B. Evidence-supported active-ingredient "
        "pair overlap across resolution levels",
        loc="left",
        fontweight="bold",
    )

    colorbar = fig.colorbar(
        image,
        ax=ax2,
        fraction=0.025,
        pad=0.02,
    )

    colorbar.set_label(
        "Documented overlap score"
    )

    ax2.text(
        0.0,
        -0.17,
        "* documented overlap changes across R0–R2\n"
        "† sensitive to fully unresolved-product evidence",
        transform=ax2.transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )

    # ============================================================
    # GLOBAL TEXT
    # ============================================================

    fig.suptitle(
        "Evidence-aware multiresolution convergence of "
        "pharmaceutical packaging dependencies",
        fontsize=15,
        fontweight="bold",
    )

    fig.text(
        0.5,
        -0.01,
        "Frozen proof-of-concept sample: "
        "9 products, 4 active ingredients. "
        "Observed overlap does not establish common suppliers, "
        "mandatory dependence, non-substitutability, "
        "or a common failure mode.",
        ha="center",
        fontsize=9,
    )

    output_path = Path(
        output_path
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "summary_json"
    )

    parser.add_argument(
        "--out",
        default=(
            "docs/figures/"
            "poc_main_results_v0_2.png"
        ),
    )

    args = parser.parse_args()

    summary = load_summary(
        args.summary_json
    )

    make_figure(
        summary,
        args.out,
    )

    print(
        "POC MAIN FIGURE WRITTEN TO",
        args.out,
    )


if __name__ == "__main__":
    main()