from pharma_resilience.robustness_bounds import (
    compute_facility_robustness_bounds,
)


def test_nonmandatory_facility_has_zero_lower_bound():
    graph = {
        "resolved_entities": {
            "F1": {
                "product_ids": ["p1", "p2"],
                "active_ingredients": [
                    "drug_a",
                    "drug_b",
                ],
                "mandatory_product_dependency_established": False,
            }
        }
    }

    result = compute_facility_robustness_bounds(
        graph
    )

    facility = result[
        "facility_bounds"
    ]["F1"]

    assert (
        facility["product_impact_lower"]
        == 0
    )

    assert (
        facility["product_impact_upper"]
        == 2
    )

    assert (
        facility["ingredient_impact_lower"]
        == 0
    )

    assert (
        facility["ingredient_impact_upper"]
        == 2
    )


def test_possible_cross_ingredient_is_not_certain():
    graph = {
        "resolved_entities": {
            "F1": {
                "product_ids": ["p1", "p2"],
                "active_ingredients": [
                    "drug_a",
                    "drug_b",
                ],
                "mandatory_product_dependency_established": False,
            }
        }
    }

    result = compute_facility_robustness_bounds(
        graph
    )

    facility = result[
        "facility_bounds"
    ]["F1"]

    assert (
        facility[
            "cross_ingredient_impact_possible"
        ]
        is True
    )

    assert (
        facility[
            "cross_ingredient_impact_certain"
        ]
        is False
    )


def test_established_mandatory_dependence_collapses_bound():
    graph = {
        "resolved_entities": {
            "F1": {
                "product_ids": ["p1", "p2"],
                "active_ingredients": [
                    "drug_a",
                    "drug_b",
                ],
                "mandatory_product_dependency_established": True,
            }
        }
    }

    result = compute_facility_robustness_bounds(
        graph
    )

    facility = result[
        "facility_bounds"
    ]["F1"]

    assert (
        facility["product_impact_lower"]
        == 2
    )

    assert (
        facility["product_impact_upper"]
        == 2
    )

    assert (
        facility[
            "cross_ingredient_impact_certain"
        ]
        is True
    )


def test_empty_graph_is_valid():
    result = compute_facility_robustness_bounds(
        {
            "resolved_entities": {}
        }
    )

    assert (
        result["n_resolved_facilities"]
        == 0
    )

    assert (
        result["max_possible_product_impact"]
        == 0
    )

    assert (
        result["max_possible_ingredient_impact"]
        == 0
    )