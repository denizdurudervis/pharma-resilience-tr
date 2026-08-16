from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .route_robustness import (
    expected_routes_remaining,
    gap_is_informative,
    targeted_routes_remaining,
)


UNKNOWN_VALUES = {
    "",
    "unknown",
    "indeterminate",
    "none",
    "na",
    "n/a",
}


def _canonical(value: str | None) -> str:
    value = (value or "").strip()
    if value.casefold() in UNKNOWN_VALUES:
        return "unknown"
    return value


def _is_known(value: str | None) -> bool:
    return _canonical(value) != "unknown"


def _present(row: dict[str, str]) -> bool:
    return (row.get("field_present") or "").strip().casefold() in {
        "1",
        "true",
        "yes",
    }


def _fraction(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(
        sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0]),
        )
    )


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _route_group_summary(
    products: list[dict[str, str]],
    group_field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)

    for product in products:
        groups[_canonical(product.get(group_field))].append(product)

    output: dict[str, dict[str, Any]] = {}

    for group_name, group_products in sorted(groups.items()):
        n_products = len(group_products)

        known_routes = [
            _canonical(product.get("route_signature"))
            for product in group_products
            if _is_known(product.get("route_signature"))
        ]

        route_counts = Counter(known_routes)
        n_known = len(known_routes)
        complete = n_known == n_products

        max_multiplicity = max(route_counts.values(), default=0)

        group_result: dict[str, Any] = {
            "n_products": n_products,
            "n_known_routes": n_known,
            "route_coverage_fraction": _fraction(n_known, n_products),
            "complete_route_observation": complete,
            "route_counts": _counter_dict(route_counts),
            "max_route_multiplicity": max_multiplicity,
            "gap_evaluable_on_observed_routes": (
                gap_is_informative(known_routes) if known_routes else False
            ),
            "random_curve": None,
            "targeted_curve": None,
        }

        if complete and known_routes:
            group_result["random_curve"] = [
                [k, expected_routes_remaining(known_routes, k)]
                for k in range(1, len(known_routes) + 1)
            ]

            group_result["targeted_curve"] = [
                [k, targeted_routes_remaining(known_routes, k)]
                for k in range(1, len(known_routes) + 1)
            ]

        output[group_name] = group_result

    return output


def summarize_audit(
    product_csv: str | Path,
    evidence_csv: str | Path,
) -> dict[str, Any]:
    products = read_csv(product_csv)
    evidence = read_csv(evidence_csv)

    n_products = len(products)

    product_ids = {
        (product.get("product_id") or "").strip()
        for product in products
    }

    ingredient_counts = Counter(
        _canonical(product.get("active_ingredient"))
        for product in products
    )

    process_counts = Counter(
        _canonical(product.get("process_class"))
        for product in products
    )

    container_counts = Counter(
        _canonical(product.get("container_class"))
        for product in products
    )

    closure_counts = Counter(
        _canonical(product.get("closure_class"))
        for product in products
    )

    route_counts = Counter(
        _canonical(product.get("route_signature"))
        for product in products
    )

    known_routes = [
        _canonical(product.get("route_signature"))
        for product in products
        if _is_known(product.get("route_signature"))
    ]

    route_ingredients: dict[str, set[str]] = defaultdict(set)

    for product in products:
        if not _is_known(product.get("route_signature")):
            continue

        route = _canonical(product.get("route_signature"))
        ingredient = _canonical(product.get("active_ingredient"))

        route_ingredients[route].add(ingredient)

    cross_ingredient_routes = {
        route: {
            "n_products": route_counts[route],
            "n_active_ingredients": len(ingredients),
            "active_ingredients": sorted(ingredients),
        }
        for route, ingredients in sorted(route_ingredients.items())
    }

    process_container_counts = Counter(
        f"{_canonical(product.get('process_class'))} × "
        f"{_canonical(product.get('container_class'))}"
        for product in products
    )

    kub_products = {
        row["product_id"]
        for row in evidence
        if (row.get("document_type") or "").strip().upper() == "KUB"
    }

    kt_products = {
        row["product_id"]
        for row in evidence
        if (row.get("document_type") or "").strip().upper() == "KT"
    }

    both_documents = kub_products & kt_products
    neither_documents = product_ids - (kub_products | kt_products)

    field_names = [
        "active_ingredient",
        "pharmaceutical_form",
        "therapeutic_indication",
        "atc_code",
        "container_class",
        "closure_class",
        "marketing_authorisation_holder",
        "license_id",
        "manufacturing_site",
        "site_role",
        "site_list_exhaustiveness",
    ]

    evidence_field_coverage: dict[str, dict[str, float | int]] = {}

    for field_name in field_names:
        observed_products = {
            row["product_id"]
            for row in evidence
            if (row.get("field_name") or "").strip() == field_name
            and _present(row)
        }

        evidence_field_coverage[field_name] = {
            "n_products": len(observed_products),
            "fraction": _fraction(len(observed_products), n_products),
        }

    sites_by_product: dict[str, set[str]] = defaultdict(set)

    for row in evidence:
        if (
            (row.get("field_name") or "").strip()
            == "manufacturing_site"
            and _present(row)
            and _is_known(row.get("observed_value"))
        ):
            sites_by_product[row["product_id"]].add(
                (row.get("observed_value") or "").strip()
            )

    products_with_named_site = len(sites_by_product)

    products_with_multiple_named_sites = sum(
        len(sites) >= 2
        for sites in sites_by_product.values()
    )

    portal_no_match_products = {
        row["product_id"]
        for row in evidence
        if (row.get("field_name") or "").strip()
        == "public_kubkt_record"
        and not _present(row)
    }

    complete_route_observation = len(known_routes) == n_products

    summary: dict[str, Any] = {
        "n_products": n_products,
        "ingredient_counts": _counter_dict(ingredient_counts),
        "process_counts": _counter_dict(process_counts),
        "container_counts": _counter_dict(container_counts),
        "closure_counts": _counter_dict(closure_counts),
        "route_counts": _counter_dict(route_counts),

        "route_observation": {
            "n_known": len(known_routes),
            "n_unknown": n_products - len(known_routes),
            "known_fraction": _fraction(
                len(known_routes),
                n_products,
            ),
            "complete_route_observation": (
                complete_route_observation
            ),
            "max_observed_route_multiplicity": max(
                Counter(known_routes).values(),
                default=0,
            ),
            "gap_evaluable_on_observed_routes": (
                gap_is_informative(known_routes)
                if known_routes
                else False
            ),
            "full_sample_gap_evaluable": (
                complete_route_observation
                and gap_is_informative(known_routes)
            ),
        },

        "cross_ingredient_routes": cross_ingredient_routes,

        "process_container_counts": _counter_dict(
            process_container_counts
        ),

        "document_availability": {
            "kub_products": len(kub_products),
            "kt_products": len(kt_products),
            "both_kub_and_kt": len(both_documents),
            "neither_kub_nor_kt": len(neither_documents),
            "portal_no_match_products": len(
                portal_no_match_products
            ),
        },

        "evidence_field_coverage": evidence_field_coverage,

        "site_observability": {
            "products_with_named_site": products_with_named_site,
            "named_site_fraction": _fraction(
                products_with_named_site,
                n_products,
            ),
            "products_with_multiple_named_sites": (
                products_with_multiple_named_sites
            ),
            "site_counts_by_product": {
                product_id: len(sites)
                for product_id, sites in sorted(
                    sites_by_product.items()
                )
            },
        },

        "route_groups": {
            "active_ingredient": _route_group_summary(
                products,
                "active_ingredient",
            ),
            "clinical_family": _route_group_summary(
                products,
                "clinical_family",
            ),
        },
    }

    return summary


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def render_markdown(summary: dict[str, Any]) -> str:
    n = summary["n_products"]
    docs = summary["document_availability"]
    route_obs = summary["route_observation"]
    sites = summary["site_observability"]

    lines: list[str] = []

    lines.append("# Audit Summary v0.1")
    lines.append("")
    lines.append(
        "Frozen 9-product audit sample; summary generated "
        "directly from the committed manual audit tables."
    )
    lines.append("")

    lines.append("## Sample")
    lines.append("")
    lines.append(f"- Products: **{n}**")
    lines.append(
        f"- Products with both KÜB and KT evidence: "
        f"**{docs['both_kub_and_kt']}/{n}**"
    )
    lines.append(
        f"- Products with neither KÜB nor KT evidence: "
        f"**{docs['neither_kub_nor_kt']}/{n}**"
    )
    lines.append(
        f"- Portal exact-search no-match observations: "
        f"**{docs['portal_no_match_products']}**"
    )
    lines.append("")

    lines.append("## Process classes")
    lines.append("")
    for key, value in summary["process_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")

    lines.append("## Container classes")
    lines.append("")
    for key, value in summary["container_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")

    lines.append("## Process × container")
    lines.append("")
    for key, value in summary[
        "process_container_counts"
    ].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")

    lines.append("## Route observation")
    lines.append("")
    lines.append(
        f"- Known route signatures: "
        f"**{route_obs['n_known']}/{n} "
        f"({_pct(route_obs['known_fraction'])})**"
    )
    lines.append(
        f"- Complete route observation: "
        f"**{route_obs['complete_route_observation']}**"
    )
    lines.append(
        f"- Maximum observed route multiplicity: "
        f"**{route_obs['max_observed_route_multiplicity']}**"
    )
    lines.append(
        f"- Robustness-gap evaluable on observed routes: "
        f"**{route_obs['gap_evaluable_on_observed_routes']}**"
    )
    lines.append(
        f"- Robustness-gap evaluable on full sample: "
        f"**{route_obs['full_sample_gap_evaluable']}**"
    )
    lines.append("")

    lines.append("## Cross-ingredient route convergence")
    lines.append("")
    lines.append(
        "| Route | Products | Active ingredients | Ingredients |"
    )
    lines.append("|---|---:|---:|---|")

    for route, values in summary[
        "cross_ingredient_routes"
    ].items():
        ingredients = ", ".join(
            values["active_ingredients"]
        )

        lines.append(
            f"| `{route}` | "
            f"{values['n_products']} | "
            f"{values['n_active_ingredients']} | "
            f"{ingredients} |"
        )

    lines.append("")

    lines.append("## Manufacturing-site observability")
    lines.append("")
    lines.append(
        f"- Products with at least one named production site: "
        f"**{sites['products_with_named_site']}/{n} "
        f"({_pct(sites['named_site_fraction'])})**"
    )
    lines.append(
        f"- Products with multiple named production sites: "
        f"**{sites['products_with_multiple_named_sites']}**"
    )
    lines.append("")

    lines.append("## Evidence-field coverage")
    lines.append("")
    lines.append("| Field | Products observed | Coverage |")
    lines.append("|---|---:|---:|")

    for field_name, values in summary[
        "evidence_field_coverage"
    ].items():
        lines.append(
            f"| `{field_name}` | "
            f"{values['n_products']}/{n} | "
            f"{_pct(values['fraction'])} |"
        )

    lines.append("")
    lines.append("## Route groups by active ingredient")
    lines.append("")

    for ingredient, values in summary[
        "route_groups"
    ]["active_ingredient"].items():
        lines.append(f"### {ingredient}")
        lines.append("")
        lines.append(
            f"- Products: {values['n_products']}"
        )
        lines.append(
            f"- Known route signatures: "
            f"{values['n_known_routes']}/"
            f"{values['n_products']}"
        )
        lines.append(
            f"- Complete route observation: "
            f"{values['complete_route_observation']}"
        )
        lines.append(
            f"- Maximum route multiplicity: "
            f"{values['max_route_multiplicity']}"
        )
        lines.append(
            f"- Gap evaluable on observed routes: "
            f"{values['gap_evaluable_on_observed_routes']}"
        )
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize the frozen pharmaceutical audit."
    )

    parser.add_argument("product_csv")
    parser.add_argument("evidence_csv")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")

    args = parser.parse_args()

    summary = summarize_audit(
        args.product_csv,
        args.evidence_csv,
    )

    markdown = render_markdown(summary)
    print(markdown)

    if args.json_out:
        output = Path(args.json_out)
        output.parent.mkdir(parents=True, exist_ok=True)
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
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            markdown + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()