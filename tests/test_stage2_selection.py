import pytest

from pharma_resilience.route_system import (
    coarsen_pharmaceutical_form,
    effective_number_from_counts,
)

from pharma_resilience.stage2_selection import (
    select_stage2_roles,
)


def test_tablet_refinements_collapse_to_oral_solid():
    assert (
        coarsen_pharmaceutical_form("tablet")
        == "oral_solid"
    )
    assert (
        coarsen_pharmaceutical_form(
            "film_coated_tablet"
        )
        == "oral_solid"
    )


def test_injection_and_infusion_solution_collapse():
    assert (
        coarsen_pharmaceutical_form(
            "injection_solution"
        )
        == "parenteral_solution"
    )
    assert (
        coarsen_pharmaceutical_form(
            "infusion_solution"
        )
        == "parenteral_solution"
    )


def test_unknown_is_explicit():
    assert (
        coarsen_pharmaceutical_form(
            "unknown_form"
        )
        == "unknown_system"
    )


def test_unmapped_form_is_not_guessed():
    with pytest.raises(KeyError):
        coarsen_pharmaceutical_form(
            "invented_form"
        )


def test_effective_number():
    assert effective_number_from_counts(
        [10]
    ) == pytest.approx(1.0)

    assert effective_number_from_counts(
        [10, 10]
    ) == pytest.approx(2.0)


def test_stage2_role_selection():
    metrics = [
        {
            "family": "FAM_SGLT2",
            "n": 48,
            "unknown": 0,
            "fine_forms": 1,
            "coarse_systems": 1,
            "coarse_eff": 1.000,
        },
        {
            "family": "FAM_STATINS",
            "n": 168,
            "unknown": 0,
            "fine_forms": 3,
            "coarse_systems": 1,
            "coarse_eff": 1.000,
        },
        {
            "family": "FAM_BISPHOSPHONATE",
            "n": 90,
            "unknown": 2,
            "fine_forms": 8,
            "coarse_systems": 4,
            "coarse_eff": 2.764,
        },
        {
            "family": "FAM_BENZO_SEIZURE",
            "n": 42,
            "unknown": 0,
            "fine_forms": 5,
            "coarse_systems": 3,
            "coarse_eff": 2.384,
        },
    ]

    selected = select_stage2_roles(metrics)

    assert (
        selected[
            "homogeneous_falsification"
        ]["family"]
        == "FAM_SGLT2"
    )

    assert (
        selected[
            "heterogeneous_stress_test"
        ]["family"]
        == "FAM_BISPHOSPHONATE"
    )
