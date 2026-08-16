import csv

import pytest

from pharma_resilience.resolved_site_graph import (
    build_resolution_map,
    build_resolved_site_graph,
)


def _write_csv(
    path,
    fieldnames,
    rows,
):
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


def test_manual_same_entity_merges_mentions(
    tmp_path,
):
    product_path = (
        tmp_path / "products.csv"
    )

    evidence_path = (
        tmp_path / "evidence.csv"
    )

    decisions_path = (
        tmp_path / "decisions.csv"
    )

    _write_csv(
        product_path,
        [
            "product_id",
            "product_name",
            "active_ingredient",
        ],
        [
            {
                "product_id": "p1",
                "product_name": "Product A",
                "active_ingredient": "drug_a",
            },
            {
                "product_id": "p2",
                "product_name": "Product B",
                "active_ingredient": "drug_b",
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
                "observed_value": "Old Name, Address 1",
            },
            {
                "product_id": "p2",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": "New Name, Address 1",
            },
        ],
    )

    _write_csv(
        decisions_path,
        [
            "left_raw_mention",
            "right_raw_mention",
            "decision",
            "resolved_entity_id",
            "confidence",
            "evidence_basis",
            "notes",
        ],
        [
            {
                "left_raw_mention": (
                    "Old Name, Address 1"
                ),
                "right_raw_mention": (
                    "New Name, Address 1"
                ),
                "decision": (
                    "same_entity_temporal_alias"
                ),
                "resolved_entity_id": (
                    "FACILITY_001"
                ),
                "confidence": "high",
                "evidence_basis": (
                    "documented_alias"
                ),
                "notes": "",
            },
        ],
    )

    result = build_resolved_site_graph(
        product_path,
        evidence_path,
        decisions_path,
    )

    assert (
        result[
            "n_resolved_facility_entities"
        ]
        == 1
    )

    facility = result[
        "resolved_entities"
    ]["FACILITY_001"]

    assert facility["n_products"] == 2

    assert (
        facility["n_active_ingredients"]
        == 2
    )

    assert (
        facility["single_failure_entity"]
        is True
    )

    assert (
        facility[
            "mandatory_product_dependency_established"
        ]
        is False
    )

    assert (
        facility[
            "direct_interdiction_ready"
        ]
        is False
    )


def test_unresolved_pair_is_not_merged(
    tmp_path,
):
    product_path = (
        tmp_path / "products.csv"
    )

    evidence_path = (
        tmp_path / "evidence.csv"
    )

    decisions_path = (
        tmp_path / "decisions.csv"
    )

    _write_csv(
        product_path,
        [
            "product_id",
            "product_name",
            "active_ingredient",
        ],
        [
            {
                "product_id": "p1",
                "product_name": "A",
                "active_ingredient": "drug_a",
            },
            {
                "product_id": "p2",
                "product_name": "B",
                "active_ingredient": "drug_b",
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
                "observed_value": "Company X",
            },
            {
                "product_id": "p2",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": (
                    "Company X, Facility Address"
                ),
            },
        ],
    )

    _write_csv(
        decisions_path,
        [
            "left_raw_mention",
            "right_raw_mention",
            "decision",
            "resolved_entity_id",
            "confidence",
            "evidence_basis",
            "notes",
        ],
        [
            {
                "left_raw_mention": "Company X",
                "right_raw_mention": (
                    "Company X, Facility Address"
                ),
                "decision": "unresolved",
                "resolved_entity_id": "",
                "confidence": "",
                "evidence_basis": (
                    "insufficient"
                ),
                "notes": "",
            },
        ],
    )

    result = build_resolved_site_graph(
        product_path,
        evidence_path,
        decisions_path,
    )

    assert (
        result[
            "n_resolved_facility_entities"
        ]
        == 0
    )

    assert (
        result[
            "n_unresolved_raw_mentions"
        ]
        == 2
    )

    assert (
        result[
            "n_cross_ingredient_resolved_facilities"
        ]
        == 0
    )


def test_unreviewed_site_remains_unresolved(
    tmp_path,
):
    product_path = (
        tmp_path / "products.csv"
    )

    evidence_path = (
        tmp_path / "evidence.csv"
    )

    decisions_path = (
        tmp_path / "decisions.csv"
    )

    _write_csv(
        product_path,
        [
            "product_id",
            "product_name",
            "active_ingredient",
        ],
        [
            {
                "product_id": "p1",
                "product_name": "A",
                "active_ingredient": "drug_a",
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
                "observed_value": (
                    "Independent Site"
                ),
            },
        ],
    )

    _write_csv(
        decisions_path,
        [
            "left_raw_mention",
            "right_raw_mention",
            "decision",
            "resolved_entity_id",
            "confidence",
            "evidence_basis",
            "notes",
        ],
        [],
    )

    result = build_resolved_site_graph(
        product_path,
        evidence_path,
        decisions_path,
    )

    assert (
        result[
            "n_resolved_facility_entities"
        ]
        == 0
    )

    assert (
        result[
            "n_unresolved_raw_mentions"
        ]
        == 1
    )


def test_conflicting_entity_assignments_raise():
    decisions = [
        {
            "left_raw_mention": "Site A",
            "right_raw_mention": "Alias A",
            "decision": "same_entity",
            "resolved_entity_id": "FACILITY_001",
        },
        {
            "left_raw_mention": "Site A",
            "right_raw_mention": "Alias B",
            "decision": "same_entity",
            "resolved_entity_id": "FACILITY_002",
        },
    ]

    with pytest.raises(
        ValueError
    ):
        build_resolution_map(
            decisions
        )