import csv

from pharma_resilience.audit_summary import (
    render_markdown,
    summarize_audit,
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


def test_audit_summary_counts_and_observability(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    product_fields = [
        "product_id",
        "active_ingredient",
        "clinical_family",
        "process_class",
        "container_class",
        "closure_class",
        "route_signature",
    ]

    products = [
        {
            "product_id": "p1",
            "active_ingredient": "famotidine",
            "clinical_family": "acid",
            "process_class": "liquid",
            "container_class": "ampoule",
            "closure_class": "unknown",
            "route_signature": "liquid|ampoule",
        },
        {
            "product_id": "p2",
            "active_ingredient": "pantoprazole",
            "clinical_family": "acid",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "route_signature": "lyophilized|vial",
        },
        {
            "product_id": "p3",
            "active_ingredient": "pantoprazole",
            "clinical_family": "acid",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
            "route_signature": "lyophilized|vial",
        },
        {
            "product_id": "p4",
            "active_ingredient": "omeprazole",
            "clinical_family": "acid",
            "process_class": "unknown",
            "container_class": "unknown",
            "closure_class": "unknown",
            "route_signature": "unknown",
        },
    ]

    evidence_fields = [
        "product_id",
        "document_type",
        "field_name",
        "field_present",
        "observed_value",
    ]

    evidence = [
        {
            "product_id": "p1",
            "document_type": "KUB",
            "field_name": "active_ingredient",
            "field_present": "1",
            "observed_value": "famotidine",
        },
        {
            "product_id": "p1",
            "document_type": "KT",
            "field_name": "manufacturing_site",
            "field_present": "1",
            "observed_value": "site A",
        },
        {
            "product_id": "p2",
            "document_type": "KUB",
            "field_name": "closure_class",
            "field_present": "1",
            "observed_value": "bromobutyl",
        },
        {
            "product_id": "p2",
            "document_type": "KT",
            "field_name": "manufacturing_site",
            "field_present": "1",
            "observed_value": "site B",
        },
        {
            "product_id": "p2",
            "document_type": "KT",
            "field_name": "manufacturing_site",
            "field_present": "1",
            "observed_value": "site C",
        },
        {
            "product_id": "p3",
            "document_type": "KUB",
            "field_name": "closure_class",
            "field_present": "1",
            "observed_value": "bromobutyl",
        },
        {
            "product_id": "p3",
            "document_type": "KT",
            "field_name": "manufacturing_site",
            "field_present": "1",
            "observed_value": "site D",
        },
        {
            "product_id": "p3",
            "document_type": "KT",
            "field_name": "site_role",
            "field_present": "0",
            "observed_value": "",
        },
        {
            "product_id": "p4",
            "document_type": "PORTAL_SEARCH",
            "field_name": "public_kubkt_record",
            "field_present": "0",
            "observed_value": "",
        },
    ]

    _write_csv(
        product_path,
        product_fields,
        products,
    )

    _write_csv(
        evidence_path,
        evidence_fields,
        evidence,
    )

    summary = summarize_audit(
        product_path,
        evidence_path,
    )

    assert summary["n_products"] == 4

    assert (
        summary["route_counts"][
            "lyophilized|vial"
        ]
        == 2
    )

    assert summary["route_counts"]["unknown"] == 1

    assert (
        summary["process_container_counts"][
            "lyophilized × vial"
        ]
        == 2
    )

    assert (
        summary["site_observability"][
            "products_with_named_site"
        ]
        == 3
    )

    assert (
        summary["site_observability"][
            "products_with_multiple_named_sites"
        ]
        == 1
    )

    pantoprazole = summary["route_groups"][
        "active_ingredient"
    ]["pantoprazole"]

    assert (
        pantoprazole[
            "complete_route_observation"
        ]
        is True
    )

    assert (
        pantoprazole[
            "max_route_multiplicity"
        ]
        == 2
    )

    assert (
        pantoprazole[
            "gap_evaluable_on_observed_routes"
        ]
        is True
    )


def test_incomplete_route_group_does_not_report_curves(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    _write_csv(
        product_path,
        [
            "product_id",
            "active_ingredient",
            "clinical_family",
            "process_class",
            "container_class",
            "closure_class",
            "route_signature",
        ],
        [
            {
                "product_id": "a",
                "active_ingredient": "omeprazole",
                "clinical_family": "acid",
                "process_class": "lyophilized",
                "container_class": "vial",
                "closure_class": "unknown",
                "route_signature": "lyophilized|vial",
            },
            {
                "product_id": "b",
                "active_ingredient": "omeprazole",
                "clinical_family": "acid",
                "process_class": "unknown",
                "container_class": "unknown",
                "closure_class": "unknown",
                "route_signature": "unknown",
            },
        ],
    )

    _write_csv(
        evidence_path,
        [
            "product_id",
            "document_type",
            "field_name",
            "field_present",
            "observed_value",
        ],
        [],
    )

    summary = summarize_audit(
        product_path,
        evidence_path,
    )

    omeprazole = summary["route_groups"][
        "active_ingredient"
    ]["omeprazole"]

    assert (
        omeprazole[
            "complete_route_observation"
        ]
        is False
    )

    assert omeprazole["random_curve"] is None
    assert omeprazole["targeted_curve"] is None

    assert (
        summary["route_observation"][
            "complete_route_observation"
        ]
        is False
    )

    assert (
        summary["route_observation"][
            "full_sample_gap_evaluable"
        ]
        is False
    )

    markdown = render_markdown(summary)

    assert "# Audit Summary v0.1" in markdown
    assert "omeprazole" in markdown


def test_cross_ingredient_route_convergence(
    tmp_path,
):
    product_path = tmp_path / "products.csv"
    evidence_path = tmp_path / "evidence.csv"

    _write_csv(
        product_path,
        [
            "product_id",
            "active_ingredient",
            "clinical_family",
            "process_class",
            "container_class",
            "closure_class",
            "route_signature",
        ],
        [
            {
                "product_id": "x1",
                "active_ingredient": "pantoprazol",
                "clinical_family": "acid",
                "process_class": "lyophilized",
                "container_class": "vial",
                "closure_class": "bromobutyl",
                "route_signature": "lyophilized|vial",
            },
            {
                "product_id": "x2",
                "active_ingredient": "esomeprazol",
                "clinical_family": "acid",
                "process_class": "lyophilized",
                "container_class": "vial",
                "closure_class": "bromobutyl",
                "route_signature": "lyophilized|vial",
            },
        ],
    )

    _write_csv(
        evidence_path,
        [
            "product_id",
            "document_type",
            "field_name",
            "field_present",
            "observed_value",
        ],
        [],
    )

    summary = summarize_audit(
        product_path,
        evidence_path,
    )

    route = summary["cross_ingredient_routes"][
        "lyophilized|vial"
    ]

    assert route["n_products"] == 2
    assert route["n_active_ingredients"] == 2

    assert route["active_ingredients"] == [
        "esomeprazol",
        "pantoprazol",
    ]

    assert (
        summary["route_observation"][
            "complete_route_observation"
        ]
        is True
    )

    assert (
        summary["route_observation"][
            "full_sample_gap_evaluable"
        ]
        is True
    )