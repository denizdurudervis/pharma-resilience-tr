import pytest

from pharma_resilience.component_evidence_coverage import (
    build_component_evidence_coverage,
    read_csv,
)


PRODUCT_AUDIT = "data/manual/product_audit_v0_1.csv"
COMPONENT_AUDIT = "data/manual/component_audit_v0_1.csv"


def _analysis():
    return build_component_evidence_coverage(
        read_csv(PRODUCT_AUDIT),
        read_csv(COMPONENT_AUDIT),
    )


def test_frozen_product_denominators():
    analysis = _analysis()

    assert (
        analysis["ingredient_summary"]["famotidin"][
            "n_frozen_products"
        ]
        == 3
    )

    assert (
        analysis["ingredient_summary"]["omeprazol"][
            "n_frozen_products"
        ]
        == 2
    )

    assert (
        analysis["ingredient_summary"]["pantoprazol"][
            "n_frozen_products"
        ]
        == 2
    )

    assert (
        analysis["ingredient_summary"]["esomeprazol"][
            "n_frozen_products"
        ]
        == 2
    )


def test_omeprazole_preserves_unresolved_product():
    analysis = _analysis()

    summary = analysis[
        "ingredient_summary"
    ]["omeprazol"]

    assert (
        summary[
            "n_products_with_any_explicit_component"
        ]
        == 1
    )

    assert (
        summary[
            "n_products_without_explicit_component_evidence"
        ]
        == 1
    )

    assert (
        summary[
            "products_without_explicit_component_evidence"
        ]
        == ["OMHEAL_2025_605"]
    )


def test_terminal_glass_vial_documented_support():
    analysis = _analysis()

    node = analysis["levels"]["R2_terminal"][
        "components"
    ]["glass_vial"]["ingredients"]

    assert (
        node["esomeprazol"][
            "documented_share_frozen"
        ]
        == 1.0
    )

    assert (
        node["pantoprazol"][
            "documented_share_frozen"
        ]
        == 1.0
    )

    assert (
        node["famotidin"][
            "documented_share_frozen"
        ]
        == pytest.approx(1 / 3, abs=1e-6)
    )


def test_omeprazole_glass_vial_evidence_scenario():
    analysis = _analysis()

    values = analysis["levels"]["R2_terminal"][
        "components"
    ]["glass_vial"]["ingredients"]["omeprazol"]

    assert (
        values[
            "n_documented_with_component"
        ]
        == 1
    )

    assert (
        values[
            "documented_share_frozen"
        ]
        == 0.5
    )

    assert (
        values[
            "documented_share_observed"
        ]
        == 1.0
    )

    assert (
        values[
            "unresolved_only_upper_scenario"
        ]
        == 1.0
    )


def test_no_unresolved_products_for_other_ingredients():
    analysis = _analysis()

    for ingredient in (
        "esomeprazol",
        "famotidin",
        "pantoprazol",
    ):
        assert (
            analysis[
                "ingredient_summary"
            ][ingredient][
                "n_products_without_explicit_component_evidence"
            ]
            == 0
        )