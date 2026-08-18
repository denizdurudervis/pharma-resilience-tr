import pytest

from pharma_resilience.packaging_schema import (
    OBSERVED,
    NOT_STATED,
    UNMAPPED_REVIEW,
    UNKNOWN,
    ARCHITECTURE_RULES,
    CanonicalField,
    PackagingObservation,
    applicable_core_fields,
    core_signature,
    core_evaluable,
    non_evaluable_reasons,
    specific_signature,
)


def observed(value):
    return CanonicalField(
        OBSERVED,
        value,
    )


def unresolved(state):
    return CanonicalField(
        state
    )


def test_observed_requires_value():
    with pytest.raises(ValueError):
        CanonicalField(
            OBSERVED,
            "",
        )


@pytest.mark.parametrize(
    "state",
    [
        NOT_STATED,
        UNMAPPED_REVIEW,
        UNKNOWN,
    ],
)
def test_unresolved_state_cannot_carry_value(
    state,
):
    with pytest.raises(ValueError):
        CanonicalField(
            state,
            "invented_value",
        )


def test_observed_unknown_architecture_is_rejected():
    with pytest.raises(ValueError):
        PackagingObservation(
            product_id="P0",
            source_reference="SRC",
            verbatim_text="text",
            architecture=observed(
                "invented_architecture"
            ),
            primary_pack_family=observed(
                "something"
            ),
        )


def test_blister_requires_closure_barrier_slot():
    with pytest.raises(ValueError):
        PackagingObservation(
            product_id="P1",
            source_reference="SRC",
            verbatim_text="text",
            architecture=observed(
                "blister"
            ),
            primary_pack_family=observed(
                "polymer_blister_cavity"
            ),
            closure_barrier_family=None,
        )


def test_integral_ampoule_forbids_manual_closure_slot():
    with pytest.raises(ValueError):
        PackagingObservation(
            product_id="P2",
            source_reference="SRC",
            verbatim_text="text",
            architecture=observed(
                "ampoule"
            ),
            primary_pack_family=observed(
                "glass_ampoule"
            ),
            closure_barrier_family=observed(
                "invented_closure"
            ),
        )


def test_complete_blister_signature():
    obs = PackagingObservation(
        product_id="P3",
        source_reference="SRC",
        verbatim_text="text",
        architecture=observed(
            "blister"
        ),
        primary_pack_family=observed(
            "polymer_blister_cavity"
        ),
        closure_barrier_family=observed(
            "metal_lidding_family"
        ),
    )

    signature = core_signature(obs)

    assert core_evaluable(obs) is True

    assert (
        "architecture=blister"
        in signature
    )

    assert (
        "closure_barrier_family="
        "metal_lidding_family"
        in signature
    )


@pytest.mark.parametrize(
    "state",
    [
        NOT_STATED,
        UNMAPPED_REVIEW,
        UNKNOWN,
    ],
)
def test_applicable_missing_closure_makes_signature_none(
    state,
):
    obs = PackagingObservation(
        product_id="P4",
        source_reference="SRC",
        verbatim_text="text",
        architecture=observed(
            "vial_closure"
        ),
        primary_pack_family=observed(
            "glass_vial"
        ),
        closure_barrier_family=(
            unresolved(state)
        ),
    )

    assert (
        core_signature(obs)
        is None
    )

    assert (
        core_evaluable(obs)
        is False
    )


def test_ampoule_has_no_artificial_na_token():
    obs = PackagingObservation(
        product_id="P5",
        source_reference="SRC",
        verbatim_text="text",
        architecture=observed(
            "ampoule"
        ),
        primary_pack_family=observed(
            "glass_ampoule"
        ),
        closure_barrier_family=None,
    )

    signature = core_signature(obs)

    assert signature is not None
    assert "NOT_APPLICABLE" not in signature

    assert applicable_core_fields(
        obs
    ) == (
        "architecture",
        "primary_pack_family",
    )


def test_missing_applicable_field_reason_is_explicit():
    obs = PackagingObservation(
        product_id="P6",
        source_reference="SRC",
        verbatim_text="text",
        architecture=observed(
            "blister"
        ),
        primary_pack_family=observed(
            "polymer_blister_cavity"
        ),
        closure_barrier_family=unresolved(
            NOT_STATED
        ),
    )

    assert non_evaluable_reasons(
        obs
    ) == (
        (
            "closure_barrier_family",
            NOT_STATED,
        ),
    )


def test_device_does_not_change_primary_core_signature():
    base = PackagingObservation(
        product_id="P7",
        source_reference="SRC",
        verbatim_text="text",
        architecture=observed(
            "vial_closure"
        ),
        primary_pack_family=observed(
            "glass_vial"
        ),
        closure_barrier_family=observed(
            "bromobutyl_stoppered_"
            "aluminium_seal_family"
        ),
    )

    detailed = PackagingObservation(
        product_id="P7",
        source_reference="SRC",
        verbatim_text="text",
        architecture=base.architecture,
        primary_pack_family=(
            base.primary_pack_family
        ),
        closure_barrier_family=(
            base.closure_barrier_family
        ),
        device_or_copack=observed(
            "administration_device"
        ),
        optional_attributes={
            "stopper_colour": "red",
        },
    )

    assert (
        core_signature(base)
        == core_signature(detailed)
    )

    assert (
        specific_signature(base)
        != specific_signature(detailed)
    )


def test_architecture_rules_are_explicit():
    assert (
        ARCHITECTURE_RULES[
            "blister"
        ][
            "closure_barrier_applicable"
        ]
        is True
    )

    assert (
        ARCHITECTURE_RULES[
            "ampoule"
        ][
            "closure_barrier_applicable"
        ]
        is False
    )
