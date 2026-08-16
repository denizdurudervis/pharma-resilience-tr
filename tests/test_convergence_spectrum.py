from pharma_resilience.convergence_spectrum import (
    build_convergence_spectrum,
    is_placeholder_dependency,
)


def test_cross_ingredient_node_is_detected():
    graph = {
        "product_nodes": {
            "p1": {
                "active_ingredient": "drug_a",
                "clinical_family": "family_1",
            },
            "p2": {
                "active_ingredient": "drug_b",
                "clinical_family": "family_1",
            },
        },
        "dependency_nodes": {
            "process::shared": {
                "dependency_type": "process",
                "value": "shared",
            },
            "container::a": {
                "dependency_type": "container",
                "value": "container_a",
            },
        },
        "product_dependencies": {
            "p1": [
                "process::shared",
                "container::a",
            ],
            "p2": [
                "process::shared",
            ],
        },
    }

    result = build_convergence_spectrum(
        graph
    )

    assert result[
        "n_dependency_nodes"
    ] == 2

    assert result[
        "n_informative_cross_ingredient_nodes"
    ] == 1

    node = result[
        "informative_cross_ingredient_nodes"
    ][0]

    assert node[
        "dependency_id"
    ] == "process::shared"

    assert node[
        "n_products"
    ] == 2

    assert node[
        "n_active_ingredients"
    ] == 2


def test_placeholder_cross_ingredient_is_not_informative():
    graph = {
        "product_nodes": {
            "p1": {
                "active_ingredient": "drug_a",
            },
            "p2": {
                "active_ingredient": "drug_b",
            },
        },
        "dependency_nodes": {
            "closure::unknown": {
                "dependency_type": "closure",
                "value": "unknown",
            },
        },
        "product_dependencies": {
            "p1": [
                "closure::unknown",
            ],
            "p2": [
                "closure::unknown",
            ],
        },
    }

    result = build_convergence_spectrum(
        graph
    )

    assert result[
        "n_placeholder_nodes"
    ] == 1

    assert result[
        "n_shared_non_placeholder_nodes"
    ] == 0

    assert result[
        "n_informative_cross_ingredient_nodes"
    ] == 0

    node = result[
        "all_nodes"
    ][0]

    assert node[
        "cross_ingredient"
    ] is True

    assert node[
        "informative_cross_ingredient"
    ] is False


def test_shared_single_ingredient_node_is_separated():
    graph = {
        "product_nodes": {
            "p1": {
                "active_ingredient": "drug_a",
            },
            "p2": {
                "active_ingredient": "drug_a",
            },
        },
        "dependency_nodes": {
            "container::shared": {
                "dependency_type": "container",
                "value": "shared_container",
            },
        },
        "product_dependencies": {
            "p1": [
                "container::shared",
            ],
            "p2": [
                "container::shared",
            ],
        },
    }

    result = build_convergence_spectrum(
        graph
    )

    assert result[
        "n_shared_non_placeholder_nodes"
    ] == 1

    assert result[
        "n_informative_cross_ingredient_nodes"
    ] == 0

    assert len(
        result[
            "shared_single_ingredient_nodes"
        ]
    ) == 1

    node = result[
        "shared_single_ingredient_nodes"
    ][0]

    assert node[
        "n_products"
    ] == 2

    assert node[
        "n_active_ingredients"
    ] == 1


def test_unobserved_dependency_node_is_retained():
    graph = {
        "product_nodes": {
            "p1": {
                "active_ingredient": "drug_a",
            },
        },
        "dependency_nodes": {
            "site::unused": {
                "dependency_type": "site",
                "value": "Unused Site",
            },
        },
        "product_dependencies": {
            "p1": [],
        },
    }

    result = build_convergence_spectrum(
        graph
    )

    assert result[
        "n_dependency_nodes"
    ] == 1

    node = result[
        "all_nodes"
    ][0]

    assert node[
        "n_products"
    ] == 0

    assert node[
        "n_active_ingredients"
    ] == 0

    assert node[
        "shared_across_products"
    ] is False


def test_placeholder_classifier():
    assert (
        is_placeholder_dependency(
            "closure",
            "unknown",
        )
        is True
    )

    assert (
        is_placeholder_dependency(
            "closure",
            "not_applicable_ampoule",
        )
        is True
    )

    assert (
        is_placeholder_dependency(
            "container",
            "type_I_clear_glass_vial",
        )
        is False
    )