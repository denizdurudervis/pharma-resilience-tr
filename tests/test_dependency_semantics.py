from pharma_resilience.dependency_semantics import (
    annotate_dependency_graph,
    classify_dependency_node,
)


def test_process_class_is_not_failure_entity():
    node = {
        "node_id": "process::lyophilized",
        "dependency_type": "process",
        "value": "lyophilized",
    }

    result = classify_dependency_node(node)

    assert (
        result["representation_kind"]
        == "descriptive_process_class"
    )

    assert (
        result["single_failure_entity"]
        is False
    )

    assert (
        result["direct_interdiction_ready"]
        is False
    )


def test_raw_site_mention_is_not_yet_failure_entity():
    node = {
        "node_id": "site::A",
        "dependency_type": "site",
        "value": "A",
    }

    result = classify_dependency_node(node)

    assert (
        result["representation_kind"]
        == "observed_site_mention"
    )

    assert (
        result["single_failure_entity"]
        is False
    )

    assert (
        result[
            "mandatory_product_dependency_established"
        ]
        is False
    )

    assert (
        result["direct_interdiction_ready"]
        is False
    )


def test_component_class_requires_more_resolution():
    node = {
        "node_id": "container::vial",
        "dependency_type": "container",
        "value": "vial",
    }

    result = classify_dependency_node(node)

    assert (
        result["representation_kind"]
        == "physical_component_class"
    )

    assert (
        result["single_failure_entity"]
        is False
    )

    assert (
        result["direct_interdiction_ready"]
        is False
    )


def test_graph_annotation_blocks_direct_interdiction():
    graph = {
        "dependency_nodes": {
            "process::lyophilized": {
                "node_id": "process::lyophilized",
                "dependency_type": "process",
                "value": "lyophilized",
            },

            "container::vial": {
                "node_id": "container::vial",
                "dependency_type": "container",
                "value": "vial",
            },

            "site::A": {
                "node_id": "site::A",
                "dependency_type": "site",
                "value": "A",
            },
        }
    }

    summary = annotate_dependency_graph(
        graph
    )

    assert (
        summary["n_dependency_nodes"]
        == 3
    )

    assert (
        summary["n_single_failure_entities"]
        == 0
    )

    assert (
        summary[
            "n_mandatory_dependencies_established"
        ]
        == 0
    )

    assert (
        summary["n_direct_interdiction_ready"]
        == 0
    )