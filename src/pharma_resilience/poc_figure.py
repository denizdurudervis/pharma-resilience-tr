from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


FACILITY_ID = "FACILITY_YENIBOSNA_SANAYI13_001"


def load_json(path: str):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def make_figure(
    dependency_graph_path: str,
    resolved_site_path: str,
    robustness_path: str,
    output_path: str,
) -> None:

    dependency_graph = load_json(
        dependency_graph_path
    )

    resolved_sites = load_json(
        resolved_site_path
    )

    robustness = load_json(
        robustness_path
    )

    process = dependency_graph[
        "cross_ingredient_dependencies"
    ]["process::lyophilized"]

    container = dependency_graph[
        "cross_ingredient_dependencies"
    ]["container::type_I_clear_glass_vial"]

    facility = resolved_sites[
        "resolved_entities"
    ][FACILITY_ID]

    facility_bound = robustness[
        "facility_bounds"
    ][FACILITY_ID]

    process_products = set(
        process["product_ids"]
    )

    container_products = set(
        container["product_ids"]
    )

    facility_products = set(
        facility["product_ids"]
    )

    container_within_process = (
        container_products
        <= process_products
    )

    facility_within_process = (
        facility_products
        <= process_products
    )

    facility_within_container = (
        facility_products
        <= container_products
    )

    labels = [
        "Process node\nLyophilized",
        "Container node\nType-I clear glass vial",
        "Resolved facility node\nYenibosna",
    ]

    product_counts = [
        process["n_products"],
        container["n_products"],
        facility["n_products"],
    ]

    ingredient_counts = [
        process["n_active_ingredients"],
        container["n_active_ingredients"],
        facility["n_active_ingredients"],
    ]

    x = list(range(len(labels)))
    width = 0.34

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    product_bars = ax.bar(
        [i - width / 2 for i in x],
        product_counts,
        width=width,
        label="Observed products",
    )

    ingredient_bars = ax.bar(
        [i + width / 2 for i in x],
        ingredient_counts,
        width=width,
        label="Active ingredients",
    )

    ax.set_xticks(
        x,
        labels,
    )

    ax.set_ylabel(
        "Observed count"
    )

    ax.set_title(
        "Selected cross-ingredient convergence signals\n"
        "across dependency layers"
    )

    ax.legend(
        loc="upper left"
    )

    for bars in (
        product_bars,
        ingredient_bars,
    ):
        for bar in bars:
            ax.text(
                bar.get_x()
                + bar.get_width() / 2,
                bar.get_height() + 0.08,
                str(int(bar.get_height())),
                ha="center",
                va="bottom",
            )

    bound_text = (
        "Resolved-facility evidence bound\n"
        f"Products: "
        f"{facility_bound['product_impact_lower']}"
        "–"
        f"{facility_bound['product_impact_upper']}\n"
        f"Active ingredients: "
        f"{facility_bound['ingredient_impact_lower']}"
        "–"
        f"{facility_bound['ingredient_impact_upper']}"
    )

    ax.text(
        0.98,
        0.91,
        bound_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
    )

    relation_text = (
        "Observed set relations\n"
        f"Vial subset of lyophilized: "
        f"{'Yes' if container_within_process else 'No'}\n"
        f"Facility subset of lyophilized: "
        f"{'Yes' if facility_within_process else 'No'}\n"
        f"Facility subset of vial: "
        f"{'Yes' if facility_within_container else 'No'}"
    )

    ax.text(
        0.98,
        0.61,
        relation_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
    )

    ax.set_ylim(
        0,
        max(product_counts) + 2.0,
    )

    fig.tight_layout()

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output,
        dpi=220,
    )

    plt.close(fig)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "dependency_graph"
    )

    parser.add_argument(
        "resolved_site_graph"
    )

    parser.add_argument(
        "robustness_bounds"
    )

    parser.add_argument(
        "--out",
        default=(
            "docs/figures/"
            "poc_convergence_layers_v0_2.png"
        ),
    )

    args = parser.parse_args()

    make_figure(
        args.dependency_graph,
        args.resolved_site_graph,
        args.robustness_bounds,
        args.out,
    )


if __name__ == "__main__":
    main()