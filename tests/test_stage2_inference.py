from pharma_resilience.stage2_inference import (
    VARIATION,
    COLLAPSE,
    INDETERMINATE,
    NOT_EVALUABLE,
    classify_within_form_stratum,
    primary_family_summary,
    common_k,
)


def test_two_observed_signatures_are_variation():
    result = classify_within_form_stratum(
        [
            "A",
            "A",
            "B",
        ]
    )

    assert result["verdict"] == VARIATION
    assert result["n_distinct_signatures"] == 2


def test_missingness_cannot_erase_observed_variation():
    result = classify_within_form_stratum(
        [
            "A",
            None,
            "B",
            None,
        ]
    )

    assert result["verdict"] == VARIATION
    assert result["n_evaluable"] == 2
    assert result["n_non_evaluable"] == 2


def test_one_signature_complete_is_collapse():
    result = classify_within_form_stratum(
        [
            "A",
            "A",
            "A",
        ]
    )

    assert result["verdict"] == COLLAPSE
    assert result["n_non_evaluable"] == 0


def test_one_signature_with_missing_is_indeterminate():
    result = classify_within_form_stratum(
        [
            "A",
            "A",
            None,
        ]
    )

    assert result["verdict"] == INDETERMINATE


def test_all_missing_is_not_evaluable():
    result = classify_within_form_stratum(
        [
            None,
            None,
        ]
    )

    assert result["verdict"] == NOT_EVALUABLE
    assert result["n_evaluable"] == 0


def test_empty_stratum_is_not_evaluable():
    result = classify_within_form_stratum(
        []
    )

    assert result["verdict"] == NOT_EVALUABLE
    assert result["n_total"] == 0


def test_family_summary_preserves_strata():
    result = primary_family_summary(
        {
            "form_a": [
                "A",
                "B",
            ],
            "form_b": [
                "C",
                "C",
            ],
            "form_c": [
                "D",
                None,
            ],
            "form_d": [
                None,
            ],
        }
    )

    assert (
        result["strata"]["form_a"]["verdict"]
        == VARIATION
    )

    assert (
        result["strata"]["form_b"]["verdict"]
        == COLLAPSE
    )

    assert (
        result["strata"]["form_c"]["verdict"]
        == INDETERMINATE
    )

    assert (
        result["strata"]["form_d"]["verdict"]
        == NOT_EVALUABLE
    )

    assert result["verdict_counts"] == {
        VARIATION: 1,
        COLLAPSE: 1,
        INDETERMINATE: 1,
        NOT_EVALUABLE: 1,
    }


def test_common_k_is_minimum_supported_depth():
    assert common_k(
        [48],
        [25, 23, 14],
    ) == 14


def test_common_k_zero_without_strata():
    assert common_k(
        [],
        [],
    ) == 0
