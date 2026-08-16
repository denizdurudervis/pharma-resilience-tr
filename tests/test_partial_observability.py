from pharma_resilience.partial_observability import (
    analyze_bounds_for_level,
)


FIELDS = (
    "process_class",
    "container_class",
    "closure_class",
)


def test_complete_data_collapses_bounds():
    rows = [
        {
            "product_id": "a",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
        },
        {
            "product_id": "b",
            "active_ingredient": "drug_b",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
        },
        {
            "product_id": "c",
            "active_ingredient": "drug_c",
            "process_class": "liquid",
            "container_class": "ampoule",
            "closure_class": "sealed",
        },
    ]

    result = analyze_bounds_for_level(
        rows,
        FIELDS,
    )

    assert result["n_complete"] == 3

    assert (
        result["largest_group_bounds"]["lower"]
        == 2
    )

    assert (
        result["largest_group_bounds"]["upper"]
        == 2
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["lower"]
        == 2
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["upper"]
        == 2
    )


def test_unknown_closure_broadens_upper_bound():
    rows = [
        {
            "product_id": "a",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
        },
        {
            "product_id": "b",
            "active_ingredient": "drug_b",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "chlorobutyl",
        },
        {
            "product_id": "c",
            "active_ingredient": "drug_c",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "unknown",
        },
    ]

    result = analyze_bounds_for_level(
        rows,
        FIELDS,
    )

    assert (
        result["largest_group_bounds"]["lower"]
        == 1
    )

    assert (
        result["largest_group_bounds"]["upper"]
        == 2
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["lower"]
        == 1
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["upper"]
        == 2
    )

    assert (
        result["certain_cross_ingredient_convergence"]
        is False
    )

    assert (
        result["possible_cross_ingredient_convergence"]
        is True
    )


def test_incompatible_known_prefixes_cannot_merge():
    rows = [
        {
            "product_id": "a",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "unknown",
        },
        {
            "product_id": "b",
            "active_ingredient": "drug_b",
            "process_class": "liquid",
            "container_class": "ampoule",
            "closure_class": "unknown",
        },
    ]

    result = analyze_bounds_for_level(
        rows,
        FIELDS,
    )

    assert (
        result["largest_group_bounds"]["upper"]
        == 1
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["upper"]
        == 1
    )

    assert (
        result["possible_cross_ingredient_convergence"]
        is False
    )


def test_multiple_unknowns_can_share_compatible_completion():
    rows = [
        {
            "product_id": "a",
            "active_ingredient": "drug_a",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "unknown",
        },
        {
            "product_id": "b",
            "active_ingredient": "drug_b",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "unknown",
        },
        {
            "product_id": "c",
            "active_ingredient": "drug_c",
            "process_class": "lyophilized",
            "container_class": "vial",
            "closure_class": "bromobutyl",
        },
    ]

    result = analyze_bounds_for_level(
        rows,
        FIELDS,
    )

    assert (
        result["largest_group_bounds"]["lower"]
        == 1
    )

    assert (
        result["largest_group_bounds"]["upper"]
        == 3
    )

    assert (
        result[
            "max_active_ingredient_span_bounds"
        ]["upper"]
        == 3
    )