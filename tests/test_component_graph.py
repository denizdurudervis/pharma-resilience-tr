from pharma_resilience.component_graph import (
    build_component_graph,
    read_component_audit,
)


AUDIT_PATH = "data/manual/component_audit_v0_1.csv"


def _graph():
    rows = read_component_audit(AUDIT_PATH)
    return build_component_graph(rows)


def test_frozen_component_audit_regression():
    graph = _graph()
    counts = graph["counts"]

    assert counts["n_audit_rows"] == 19
    assert counts["n_products"] == 9
    assert counts["n_explicit_observations"] == 18
    assert counts["n_component_classes"] == 9

    # NEVOFAM-L uses the same physical Type-I clear glass ampoule
    # in two roles, so 18 explicit observations collapse to
    # 17 unique physical product-component relationships.
    assert counts["n_unique_product_component_edges"] == 17

    assert graph["coverage"]["n_unresolved_products"] == 1
    assert graph["coverage"]["unresolved_product_ids"] == [
        "OMHEAL_2025_605"
    ]


def test_exact_cross_ingredient_component_convergence():
    graph = _graph()
    cross = graph["cross_ingredient_components"]

    assert set(cross) == {
        "type_I_clear_glass_vial",
        "bromobutyl_rubber_stopper",
        "bromobutyl_lyophilization_stopper",
    }

    vial = cross["type_I_clear_glass_vial"]

    assert vial["n_products"] == 6
    assert vial["n_active_ingredients"] == 4
    assert set(vial["active_ingredients"]) == {
        "esomeprazol",
        "famotidin",
        "omeprazol",
        "pantoprazol",
    }

    bromobutyl = cross["bromobutyl_rubber_stopper"]

    assert bromobutyl["n_products"] == 2
    assert set(bromobutyl["active_ingredients"]) == {
        "omeprazol",
        "pantoprazol",
    }

    lyophilization = cross[
        "bromobutyl_lyophilization_stopper"
    ]

    assert lyophilization["n_products"] == 2
    assert set(lyophilization["active_ingredients"]) == {
        "esomeprazol",
        "pantoprazol",
    }


def test_same_physical_component_can_have_multiple_roles():
    graph = _graph()

    matches = [
        edge
        for edge in graph["edges"]
        if edge["product_id"] == "NEVOFAML_2022_12"
        and edge["component_class"] == "type_I_clear_glass_ampoule"
    ]

    assert len(matches) == 1

    assert set(matches[0]["roles"]) == {
        "primary_container",
        "solvent_container",
    }


def test_unresolved_product_does_not_create_component_edge():
    graph = _graph()

    assert not any(
        edge["product_id"] == "OMHEAL_2025_605"
        for edge in graph["edges"]
    )