import csv

from pharma_resilience.dependency_graph import (
    build_dependency_graph,
)


def _write_csv(path, fieldnames, rows):
    with open(
        path,
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(rows)


def test_unknowns_do_not_create_shared_nodes(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    _write_csv(
        product_path,
        [
            "product_id",
            "product_name",
            "active_ingredient",
            "clinical_family",
            "process_class",
            "container_class",
            "closure_class",
        ],
        [
            {
                "product_id": "p1",
                "product_name": "A",
                "active_ingredient": "drug_a",
                "clinical_family": "x",
                "process_class": "lyophilized",
                "container_class": "vial",
                "closure_class": "unknown",
            },
            {
                "product_id": "p2",
                "product_name": "B",
                "active_ingredient": "drug_b",
                "clinical_family": "x",
                "process_class": "lyophilized",
                "container_class": "vial",
                "closure_class": "unknown",
            },
        ],
    )

    _write_csv(
        evidence_path,
        [
            "product_id",
            "field_name",
            "field_present",
            "observed_value",
        ],
        [],
    )

    graph = build_dependency_graph(
        product_path,
        evidence_path,
    )

    assert (
        "closure::unknown"
        not in graph["dependency_nodes"]
    )

    assert (
        graph[
            "cross_ingredient_dependencies"
        ]["process::lyophilized"][
            "n_active_ingredients"
        ]
        == 2
    )


def test_multiple_sites_create_multiple_edges(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    _write_csv(
        product_path,
        [
            "product_id",
            "product_name",
            "active_ingredient",
            "clinical_family",
            "process_class",
            "container_class",
            "closure_class",
        ],
        [
            {
                "product_id": "p1",
                "product_name": "A",
                "active_ingredient": "drug_a",
                "clinical_family": "x",
                "process_class": "liquid",
                "container_class": "ampoule",
                "closure_class": "unknown",
            },
        ],
    )

    _write_csv(
        evidence_path,
        [
            "product_id",
            "field_name",
            "field_present",
            "observed_value",
        ],
        [
            {
                "product_id": "p1",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": "Site A",
            },
            {
                "product_id": "p1",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": "Site B",
            },
        ],
    )

    graph = build_dependency_graph(
        product_path,
        evidence_path,
    )

    dependencies = graph[
        "product_dependencies"
    ]["p1"]

    assert "site::Site A" in dependencies
    assert "site::Site B" in dependencies


def test_shared_site_detects_cross_ingredient_dependency(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    products = [
        {
            "product_id": "p1",
            "product_name": "A",
            "active_ingredient": "drug_a",
            "clinical_family": "x",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
        },
        {
            "product_id": "p2",
            "product_name": "B",
            "active_ingredient": "drug_b",
            "clinical_family": "x",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "chlorobutyl",
        },
    ]

    _write_csv(
        product_path,
        list(products[0].keys()),
        products,
    )

    _write_csv(
        evidence_path,
        [
            "product_id",
            "field_name",
            "field_present",
            "observed_value",
        ],
        [
            {
                "product_id": "p1",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": "Shared Site",
            },
            {
                "product_id": "p2",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": "Shared Site",
            },
        ],
    )

    graph = build_dependency_graph(
        product_path,
        evidence_path,
    )

    site = graph[
        "cross_ingredient_dependencies"
    ]["site::Shared Site"]

    assert site["n_products"] == 2
    assert site["n_active_ingredients"] == 2