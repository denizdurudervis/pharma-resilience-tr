import csv

from pharma_resilience.resolution_sensitivity import (
    analyze_resolution_sensitivity,
    render_markdown,
)


FIELDS = [
    "product_id",
    "active_ingredient",
    "process_class",
    "container_class",
    "closure_class",
    "site_name",
]


def _write_products(path, rows):
    with open(
        path,
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDS,
        )
        writer.writeheader()
        writer.writerows(rows)


def test_resolution_refines_convergence_without_missingness(
    tmp_path,
):
    path = tmp_path / "products.csv"

    rows = [
        {
            "product_id": "p1",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "site_name": "site_1",
        },
        {
            "product_id": "p2",
            "active_ingredient": "drug_b",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "chlorobutyl",
            "site_name": "site_2",
        },
        {
            "product_id": "p3",
            "active_ingredient": "drug_c",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "site_name": "unknown",
        },
        {
            "product_id": "p4",
            "active_ingredient": "drug_d",
            "process_class": "liquid",
            "container_class": "ampoule",
            "closure_class": "unknown",
            "site_name": "site_3",
        },
    ]

    _write_products(path, rows)

    summary = analyze_resolution_sensitivity(
        path
    )

    r1 = summary["available_case"][
        "R1_process_container"
    ]

    shared = r1[
        "cross_ingredient_groups"
    ]["lyophilized|vial"]

    assert shared["n_products"] == 3
    assert shared["n_active_ingredients"] == 3

    r2 = summary["available_case"][
        "R2_process_container_closure"
    ]

    assert r2["n_observed_products"] == 3

    assert (
        r2["cross_ingredient_groups"][
            "lyophilized|vial|bromobutyl"
        ]["n_active_ingredients"]
        == 2
    )

    r3 = summary["available_case"][
        "R3_process_container_closure_named_site"
    ]

    assert r3["n_observed_products"] == 2
    assert r3["n_cross_ingredient_signatures"] == 0


def test_complete_case_uses_fixed_product_set(
    tmp_path,
):
    path = tmp_path / "products.csv"

    rows = [
        {
            "product_id": "p1",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "site_name": "site_1",
        },
        {
            "product_id": "p2",
            "active_ingredient": "drug_b",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "chlorobutyl",
            "site_name": "site_2",
        },
        {
            "product_id": "p3",
            "active_ingredient": "drug_c",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "site_name": "unknown",
        },
    ]

    _write_products(path, rows)

    summary = analyze_resolution_sensitivity(
        path
    )

    assert summary["complete_case_n_products"] == 2

    for level in summary[
        "complete_case"
    ].values():
        assert level["n_input_products"] == 2
        assert level["n_observed_products"] == 2

    r1 = summary["complete_case"][
        "R1_process_container"
    ]

    assert r1["n_cross_ingredient_signatures"] == 1

    r2 = summary["complete_case"][
        "R2_process_container_closure"
    ]

    assert r2["n_cross_ingredient_signatures"] == 0

    markdown = render_markdown(summary)

    assert "Available-case analysis" in markdown
    assert (
        "Complete-case resolution sensitivity"
        in markdown
    )