from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from pharma_resilience.route_robustness import (
    expected_routes_remaining,
    gap_is_informative,
    targeted_routes_remaining,
)


def drug_container_family(route_signature: str) -> str:
    """
    Classify the drug-containing primary container from the frozen
    route signature.

    Examples
    --------
    liquid|ampoule -> ampoule
    lyophilized|vial+solvent_ampoule -> vial
    lyophilized|ampoule+solvent_ampoule -> ampoule
    """
    route = route_signature.strip().lower()

    if "vial" in route:
        return "vial"
    if "ampoule" in route:
        return "ampoule"

    return "unknown"


def summarize_family(
    csv_path: str | Path,
    active_ingredient: str,
) -> dict:
    csv_path = Path(csv_path)

    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    target = active_ingredient.strip().casefold()

    family_rows = [
        row
        for row in rows
        if row["active_ingredient"].strip().casefold() == target
    ]

    routes = [
        row["route_signature"].strip()
        for row in family_rows
        if row["route_signature"].strip()
    ]

    processes = [
        row["process_class"].strip()
        for row in family_rows
        if row["process_class"].strip()
    ]

    process_counts = Counter(processes)
    route_counts = Counter(routes)

    process_container_counts = Counter(
        (
            row["process_class"].strip(),
            drug_container_family(row["route_signature"]),
        )
        for row in family_rows
    )

    n_products = len(family_rows)

    if routes:
        max_route_multiplicity = max(route_counts.values())
    else:
        max_route_multiplicity = 0

    random_curve = [
        (k, expected_routes_remaining(routes, k))
        for k in range(1, len(routes) + 1)
    ]

    targeted_curve = [
        (k, targeted_routes_remaining(routes, k))
        for k in range(1, len(routes) + 1)
    ]

    return {
        "active_ingredient": active_ingredient,
        "n_products": n_products,
        "n_process_classes": len(process_counts),
        "n_route_signatures": len(route_counts),
        "process_counts": dict(process_counts),
        "route_counts": dict(route_counts),
        "max_route_multiplicity": max_route_multiplicity,
        "robustness_gap_evaluable": gap_is_informative(routes),
        "process_container_counts": dict(process_container_counts),
        "random_curve": random_curve,
        "targeted_curve": targeted_curve,
    }


def print_summary(summary: dict) -> None:
    print("ACTIVE INGREDIENT =", summary["active_ingredient"])
    print("N PRODUCTS =", summary["n_products"])
    print("N PROCESS CLASSES =", summary["n_process_classes"])
    print("N ROUTE SIGNATURES =", summary["n_route_signatures"])
    print("PROCESS COUNTS =", summary["process_counts"])
    print("ROUTE COUNTS =", summary["route_counts"])
    print(
        "MAX ROUTE MULTIPLICITY =",
        summary["max_route_multiplicity"],
    )
    print(
        "ROBUSTNESS GAP EVALUABLE =",
        summary["robustness_gap_evaluable"],
    )
    print(
        "PROCESS x CONTAINER =",
        summary["process_container_counts"],
    )
    print("RANDOM CURVE =", summary["random_curve"])
    print("TARGETED CURVE =", summary["targeted_curve"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize a frozen pharmaceutical family audit."
    )

    parser.add_argument(
        "csv_path",
        help="Path to product_audit CSV.",
    )

    parser.add_argument(
        "active_ingredient",
        help="Active ingredient to summarize.",
    )

    args = parser.parse_args()

    summary = summarize_family(
        args.csv_path,
        args.active_ingredient,
    )

    print_summary(summary)


if __name__ == "__main__":
    main()