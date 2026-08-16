from pharma_resilience.component_resolution import (
    build_parent_map,
    build_resolution_analysis,
    read_component_audit,
    terminal_parent,
)


AUDIT_PATH = "data/manual/component_audit_v0_1.csv"


def _rows():
    return read_component_audit(AUDIT_PATH)


def _analysis():
    return build_resolution_analysis(_rows())


def test_observed_parent_chain():
    parent_map = build_parent_map(_rows())

    assert (
        parent_map[
            "bromobutyl_lyophilization_stopper"
        ]
        == "bromobutyl_rubber_stopper"
    )

    assert (
        parent_map[
            "bromobutyl_rubber_stopper"
        ]
        == "rubber_stopper"
    )

    assert (
        terminal_parent(
            "bromobutyl_lyophilization_stopper",
            parent_map,
        )
        == "rubber_stopper"
    )


def test_self_parent_is_terminal():
    parent_map = build_parent_map(_rows())

    assert parent_map["aluminium_cap"] == "aluminium_cap"

    assert (
        terminal_parent(
            "aluminium_cap",
            parent_map,
        )
        == "aluminium_cap"
    )


def test_resolution_class_counts():
    analysis = _analysis()

    assert (
        analysis["levels"]["R0_exact"]["n_component_classes"]
        == 9
    )

    # One parent step still keeps
    # bromobutyl_rubber_stopper and rubber_stopper
    # as distinct nodes.
    assert (
        analysis["levels"]["R1_parent"]["n_component_classes"]
        == 6
    )

    # Terminal aggregation collapses the full
    # bromobutyl chain to rubber_stopper.
    assert (
        analysis["levels"]["R2_terminal"]["n_component_classes"]
        == 5
    )


def test_r1_keeps_stopper_families_separate():
    analysis = _analysis()

    r1 = analysis["levels"]["R1_parent"]["component_nodes"]

    lyophilization_parent = r1[
        "bromobutyl_rubber_stopper"
    ]

    assert lyophilization_parent["n_products"] == 2
    assert lyophilization_parent["n_active_ingredients"] == 2

    assert set(
        lyophilization_parent["active_ingredients"]
    ) == {
        "esomeprazol",
        "pantoprazol",
    }

    assert set(
        lyophilization_parent["exact_component_classes"]
    ) == {
        "bromobutyl_lyophilization_stopper",
    }

    terminal_family_entry = r1["rubber_stopper"]

    assert terminal_family_entry["n_products"] == 2
    assert terminal_family_entry["n_active_ingredients"] == 2

    assert set(
        terminal_family_entry["active_ingredients"]
    ) == {
        "omeprazol",
        "pantoprazol",
    }

    assert set(
        terminal_family_entry["exact_component_classes"]
    ) == {
        "bromobutyl_rubber_stopper",
    }


def test_parent_resolution_aluminium_convergence():
    analysis = _analysis()

    node = analysis["levels"]["R1_parent"]["component_nodes"][
        "aluminium_cap"
    ]

    assert node["n_products"] == 3
    assert node["n_active_ingredients"] == 3

    assert set(node["active_ingredients"]) == {
        "esomeprazol",
        "omeprazol",
        "pantoprazol",
    }


def test_parent_resolution_ampoule_family():
    analysis = _analysis()

    node = analysis["levels"]["R1_parent"]["component_nodes"][
        "glass_ampoule"
    ]

    assert node["n_products"] == 3
    assert node["n_active_ingredients"] == 1

    assert node["active_ingredients"] == [
        "famotidin"
    ]


def test_terminal_resolution_rubber_family():
    analysis = _analysis()

    node = analysis["levels"]["R2_terminal"]["component_nodes"][
        "rubber_stopper"
    ]

    assert node["n_products"] == 4
    assert node["n_active_ingredients"] == 3

    assert set(node["active_ingredients"]) == {
        "esomeprazol",
        "omeprazol",
        "pantoprazol",
    }

    assert set(node["exact_component_classes"]) == {
        "bromobutyl_lyophilization_stopper",
        "bromobutyl_rubber_stopper",
    }


def test_edge_count_is_preserved_under_current_hierarchy():
    analysis = _analysis()

    assert (
        analysis["levels"]["R0_exact"][
            "n_product_component_edges"
        ]
        == 17
    )

    assert (
        analysis["levels"]["R1_parent"][
            "n_product_component_edges"
        ]
        == 17
    )

    assert (
        analysis["levels"]["R2_terminal"][
            "n_product_component_edges"
        ]
        == 17
    )