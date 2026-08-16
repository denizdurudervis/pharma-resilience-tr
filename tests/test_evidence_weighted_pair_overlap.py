import pytest

from pharma_resilience.component_evidence_coverage import (
    read_csv,
)
from pharma_resilience.evidence_weighted_pair_overlap import (
    build_evidence_weighted_pair_overlap,
)


PRODUCT_AUDIT = "data/manual/product_audit_v0_1.csv"
COMPONENT_AUDIT = "data/manual/component_audit_v0_1.csv"


def _analysis():
    return build_evidence_weighted_pair_overlap(
        read_csv(PRODUCT_AUDIT),
        read_csv(COMPONENT_AUDIT),
    )


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

    for pair in analysis[
        "levels"
    ][level]["pairs"]:
        if {
            pair["ingredient_a"],
            pair["ingredient_b"],
        } == wanted:
            return pair

    raise AssertionError(
        f"Pair not found: "
        f"{ingredient_a}, {ingredient_b}"
    )


def test_pair_universe_is_preserved():
    analysis = _analysis()

    assert analysis["ingredients"] == [
        "esomeprazol",
        "famotidin",
        "omeprazol",
        "pantoprazol",
    ]

    for level in analysis[
        "levels"
    ].values():
        assert level["n_pairs"] == 6


def test_terminal_esomeprazole_omeprazole_overlap():
    analysis = _analysis()

    pair = _pair(
        analysis,
        "R2_terminal",
        "esomeprazol",
        "omeprazol",
    )

    assert (
        pair[
            "existential_shared_component_count"
        ]
        == 3
    )

    assert (
        pair[
            "documented_overlap_score"
        ]
        == pytest.approx(1.5)
    )

    assert (
        pair[
            "componentwise_unresolved_envelope_score"
        ]
        == pytest.approx(2.0)
    )

    assert (
        pair["envelope_increment"]
        == pytest.approx(0.5)
    )


def test_terminal_omeprazole_pantoprazole_overlap():
    analysis = _analysis()

    pair = _pair(
        analysis,
        "R2_terminal",
        "omeprazol",
        "pantoprazol",
    )

    assert (
        pair[
            "documented_overlap_score"
        ]
        == pytest.approx(1.5)
    )

    assert (
        pair[
            "componentwise_unresolved_envelope_score"
        ]
        == pytest.approx(3.0)
    )

    assert (
        pair["envelope_increment"]
        == pytest.approx(1.5)
    )


def test_terminal_famotidine_omeprazole_uncertainty():
    analysis = _analysis()

    pair = _pair(
        analysis,
        "R2_terminal",
        "famotidin",
        "omeprazol",
    )

    assert (
        pair[
            "documented_overlap_score"
        ]
        == pytest.approx(
            1 / 3,
            abs=1e-6,
        )
    )

    assert (
        pair[
            "componentwise_unresolved_envelope_score"
        ]
        == pytest.approx(
            5 / 6,
            abs=1e-6,
        )
    )


def test_pairs_without_omeprazole_have_no_envelope_increment():
    analysis = _analysis()

    for level_name, level in analysis[
        "levels"
    ].items():
        for pair in level["pairs"]:
            if "omeprazol" not in {
                pair["ingredient_a"],
                pair["ingredient_b"],
            }:
                assert (
                    pair[
                        "envelope_increment"
                    ]
                    == pytest.approx(0.0)
                )


def test_terminal_esomeprazole_omeprazole_contributions():
    analysis = _analysis()

    pair = _pair(
        analysis,
        "R2_terminal",
        "esomeprazol",
        "omeprazol",
    )

    contributions = {
        item["component_class"]: item
        for item in pair[
            "component_contributions"
        ]
    }

    assert (
        contributions[
            "glass_vial"
        ][
            "documented_overlap_contribution"
        ]
        == pytest.approx(0.5)
    )

    assert (
        contributions[
            "rubber_stopper"
        ][
            "documented_overlap_contribution"
        ]
        == pytest.approx(0.5)
    )

    assert (
        contributions[
            "aluminium_cap"
        ][
            "documented_overlap_contribution"
        ]
        == pytest.approx(0.5)
    )

    assert (
        contributions[
            "glass_vial"
        ][
            "componentwise_envelope_contribution"
        ]
        == pytest.approx(1.0)
    )