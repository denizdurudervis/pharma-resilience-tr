import pytest

from pharma_resilience.family_selection import (
    DEFAULT_STUDY_SEED,
    deterministic_hash,
    select_families,
)


def _row(
    family_id,
    stratum,
    status="eligible",
):
    return {
        "family_id": family_id,
        "family_name": family_id,
        "clinical_context": "synthetic test",
        "eligibility_basis": "test",
        "evidence_source": "test",
        "route_form_stratum": stratum,
        "n_candidate_active_ingredients": "3",
        "n_candidate_products": "6",
        "eligibility_status": status,
        "exclusion_reason": "",
        "reviewer_note": "",
    }


def test_hash_is_deterministic():
    first = deterministic_hash(
        "FAMILY_A"
    )

    second = deterministic_hash(
        "FAMILY_A"
    )

    assert first == second

    assert len(first) == 64

    assert first == deterministic_hash(
        "FAMILY_A",
        DEFAULT_STUDY_SEED,
    )


def test_duplicate_family_id_is_rejected():
    rows = [
        _row("FAMILY_A", "H"),
        _row("FAMILY_A", "D"),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate family_id",
    ):
        select_families(rows)


def test_invalid_stratum_for_eligible_family_is_rejected():
    rows = [
        _row(
            "FAMILY_A",
            "X",
        )
    ]

    with pytest.raises(
        ValueError,
        match="must have stratum H or D",
    ):
        select_families(rows)


def test_balanced_four_plus_four_selection():
    rows = [
        *[
            _row(
                f"H_{index}",
                "H",
            )
            for index in range(1, 7)
        ],
        *[
            _row(
                f"D_{index}",
                "D",
            )
            for index in range(1, 7)
        ],
    ]

    result = select_families(
        rows
    )

    counts = result[
        "registry_counts"
    ]

    assert counts[
        "n_selected"
    ] == 8

    assert counts[
        "n_selected_H"
    ] == 4

    assert counts[
        "n_selected_D"
    ] == 4


def test_short_stratum_is_filled_from_other_stratum():
    rows = [
        _row("H_1", "H"),
        _row("H_2", "H"),
        *[
            _row(
                f"D_{index}",
                "D",
            )
            for index in range(
                1,
                9,
            )
        ],
    ]

    result = select_families(
        rows
    )

    counts = result[
        "registry_counts"
    ]

    assert counts[
        "n_selected"
    ] == 8

    assert counts[
        "n_selected_H"
    ] == 2

    assert counts[
        "n_selected_D"
    ] == 6


def test_ineligible_and_pending_families_are_not_selected():
    rows = [
        _row(
            "H_ELIGIBLE",
            "H",
            "eligible",
        ),
        _row(
            "H_INELIGIBLE",
            "H",
            "ineligible",
        ),
        _row(
            "D_PENDING",
            "D",
            "pending",
        ),
        _row(
            "D_ELIGIBLE",
            "D",
            "eligible",
        ),
    ]

    result = select_families(
        rows
    )

    selected_ids = {
        item["family_id"]
        for item in result[
            "selected_families"
        ]
    }

    assert selected_ids == {
        "H_ELIGIBLE",
        "D_ELIGIBLE",
    }


def test_selection_is_invariant_to_registry_row_order():
    rows = [
        *[
            _row(
                f"H_{index}",
                "H",
            )
            for index in range(1, 8)
        ],
        *[
            _row(
                f"D_{index}",
                "D",
            )
            for index in range(1, 8)
        ],
    ]

    result_a = select_families(
        rows
    )

    result_b = select_families(
        list(reversed(rows))
    )

    selected_a = [
        item["family_id"]
        for item in result_a[
            "selected_families"
        ]
    ]

    selected_b = [
        item["family_id"]
        for item in result_b[
            "selected_families"
        ]
    ]

    assert selected_a == selected_b