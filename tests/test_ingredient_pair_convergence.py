import pytest

from pharma_resilience.ingredient_pair_convergence import (
    build_pair_convergence,
)
from pharma_resilience.component_resolution import (
    read_component_audit,
)


AUDIT_PATH = "data/manual/component_audit_v0_1.csv"


def _analysis():
    rows = read_component_audit(AUDIT_PATH)
    return build_pair_convergence(rows)


def _pair(
    analysis,
    level,
    ingredient_a,
    ingredient_b,
):
    wanted = {
        ingredient_a,
        ingredient_b,
    }

    for pair in analysis["levels"][level]["pairs"]:
        if {
            pair["ingredient_a"],
            pair["ingredient_b"],
        } == wanted:
            return pair

    raise AssertionError(
        f"Pair not found: {ingredient_a}, {ingredient_b}"
    )


def test_frozen_ingredient_universe():
    analysis = _analysis()

    assert analysis["ingredients"] == [
        "esomeprazol",
        "famotidin",
        "omeprazol",
        "pantoprazol",
    ]

    for level in analysis["levels"].values():
        assert level["n_pairs"] == 6


def test_exact_pair_convergence_counts():
    analysis = _analysis()

    expected = {
        ("esomeprazol", "famotidin"): 1,
        ("esomeprazol", "omeprazol"): 1,
        ("esomeprazol", "pantoprazol"): 2,
        ("famotidin", "omeprazol"): 1,
        ("famotidin", "pantoprazol"): 1,
        ("omeprazol", "pantoprazol"): 2,
    }

    for ingredients, count in expected.items():
        pair = _pair(
            analysis,
            "R0_exact",
            *ingredients,
        )

        assert (
            pair["n_shared_components"]
            == count
        )


def test_r1_pair_convergence_counts():
    analysis = _analysis()

    expected = {
        ("esomeprazol", "famotidin"): 1,
        ("esomeprazol", "omeprazol"): 2,
        ("esomeprazol", "pantoprazol"): 3,
        ("famotidin", "omeprazol"): 1,
        ("famotidin", "pantoprazol"): 1,
        ("omeprazol", "pantoprazol"): 3,
    }

    for ingredients, count in expected.items():
        pair = _pair(
            analysis,
            "R1_parent",
            *ingredients,
        )

        assert (
            pair["n_shared_components"]
            == count
        )


def test_terminal_pair_convergence_counts():
    analysis = _analysis()

    expected = {
        ("esomeprazol", "famotidin"): 1,
        ("esomeprazol", "omeprazol"): 3,
        ("esomeprazol", "pantoprazol"): 3,
        ("famotidin", "omeprazol"): 1,
        ("famotidin", "pantoprazol"): 1,
        ("omeprazol", "pantoprazol"): 3,
    }

    for ingredients, count in expected.items():
        pair = _pair(
            analysis,
            "R2_terminal",
            *ingredients,
        )

        assert (
            pair["n_shared_components"]
            == count
        )


def test_terminal_esomeprazole_omeprazole_components():
    analysis = _analysis()

    pair = _pair(
        analysis,
        "R2_terminal",
        "esomeprazol",
        "omeprazol",
    )

    assert set(
        pair["shared_component_classes"]
    ) == {
        "aluminium_cap",
        "glass_vial",
        "rubber_stopper",
    }

    assert (
        pair[
            "delta_shared_from_previous_resolution"
        ]
        == 1
    )


def test_resolution_summary_means():
    analysis = _analysis()

    assert (
        analysis["levels"]["R0_exact"][
            "mean_shared_component_count"
        ]
        == pytest.approx(8 / 6)
    )

    assert (
        analysis["levels"]["R1_parent"][
            "mean_shared_component_count"
        ]
        == pytest.approx(11 / 6)
    )

    assert (
        analysis["levels"]["R2_terminal"][
            "mean_shared_component_count"
        ]
        == pytest.approx(12 / 6)
    )