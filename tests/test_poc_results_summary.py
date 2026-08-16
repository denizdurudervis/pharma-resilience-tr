import pytest

from pharma_resilience.component_evidence_coverage import (
    read_csv,
)
from pharma_resilience.poc_results_summary import (
    build_poc_results_summary,
)


PRODUCT_AUDIT = "data/manual/product_audit_v0_1.csv"
COMPONENT_AUDIT = "data/manual/component_audit_v0_1.csv"


def _summary():
    return build_poc_results_summary(
        read_csv(PRODUCT_AUDIT),
        read_csv(COMPONENT_AUDIT),
    )


def _pair(
    summary,
    ingredient_a,
    ingredient_b,
):
    wanted = {
        ingredient_a,
        ingredient_b,
    }

    for pair in summary[
        "pair_trajectories"
    ]:
        if {
            pair["ingredient_a"],
            pair["ingredient_b"],
        } == wanted:
            return pair

    raise AssertionError(
        f"Pair not found: "
        f"{ingredient_a}, {ingredient_b}"
    )


def test_frozen_dataset_summary():
    summary = _summary()

    assert summary["dataset"][
        "n_products"
    ] == 9

    assert summary["dataset"][
        "n_audit_rows"
    ] == 19

    assert summary["dataset"][
        "n_explicit_component_observations"
    ] == 18

    assert summary["dataset"][
        "unresolved_product_ids"
    ] == ["OMHEAL_2025_605"]


def test_resolution_summary():
    summary = _summary()

    r0 = summary["resolution_summary"][
        "R0_exact"
    ]
    r1 = summary["resolution_summary"][
        "R1_parent"
    ]
    r2 = summary["resolution_summary"][
        "R2_terminal"
    ]

    assert r0["n_component_classes"] == 9
    assert r1["n_component_classes"] == 6
    assert r2["n_component_classes"] == 5

    assert (
        r0["mean_documented_overlap_score"]
        == pytest.approx(0.666666)
    )

    assert (
        r1["mean_documented_overlap_score"]
        == pytest.approx(0.916666)
    )

    assert (
        r2["mean_documented_overlap_score"]
        == pytest.approx(1.0)
    )


def test_esomeprazole_omeprazole_resolution_trajectory():
    summary = _summary()

    pair = _pair(
        summary,
        "esomeprazol",
        "omeprazol",
    )

    assert (
        pair["levels"]["R0_exact"][
            "documented_overlap_score"
        ]
        == pytest.approx(0.5)
    )

    assert (
        pair["levels"]["R1_parent"][
            "documented_overlap_score"
        ]
        == pytest.approx(1.0)
    )

    assert (
        pair["levels"]["R2_terminal"][
            "documented_overlap_score"
        ]
        == pytest.approx(1.5)
    )

    assert pair[
        "resolution_sensitive"
    ] is True

    assert pair[
        "unresolved_evidence_sensitive"
    ] is True


def test_resolution_sensitive_pair_classification():
    summary = _summary()

    observed = {
        frozenset(pair)
        for pair in summary[
            "classification"
        ][
            "resolution_sensitive_pairs"
        ]
    }

    expected = {
        frozenset(
            ("esomeprazol", "omeprazol")
        ),
        frozenset(
            ("esomeprazol", "pantoprazol")
        ),
        frozenset(
            ("omeprazol", "pantoprazol")
        ),
    }

    assert observed == expected


def test_unresolved_evidence_sensitivity_is_confined_to_omeprazole_pairs():
    summary = _summary()

    sensitive = {
        frozenset(pair)
        for pair in summary[
            "classification"
        ][
            "unresolved_evidence_sensitive_pairs"
        ]
    }

    expected = {
        frozenset(
            ("esomeprazol", "omeprazol")
        ),
        frozenset(
            ("famotidin", "omeprazol")
        ),
        frozenset(
            ("omeprazol", "pantoprazol")
        ),
    }

    assert sensitive == expected


def test_strongest_terminal_documented_pair():
    summary = _summary()

    strongest = summary[
        "strongest_terminal_documented_overlap"
    ]

    assert strongest[
        "score"
    ] == pytest.approx(2.0)

    assert {
        frozenset(pair)
        for pair in strongest["pairs"]
    } == {
        frozenset(
            ("esomeprazol", "pantoprazol")
        )
    }