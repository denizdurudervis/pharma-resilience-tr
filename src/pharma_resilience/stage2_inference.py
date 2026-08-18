"""
Frozen Stage-2 primary inference contract.

Primary inference is WITHIN fine pharmaceutical-form strata.

Canonical packaging signatures must not be pooled across fine forms
for the primary result.

Raw signature richness must not be compared directly between
Stage-2 arms.

Cross-arm magnitude comparisons, if later performed, are secondary
and require a common-k sampling / rarefaction design.

Primary coding resolution:
    canonical core packaging signature

Sensitivity coding resolution:
    verbatim wording and/or specific optional attributes
"""


VARIATION = "variation"
COLLAPSE = "collapse"
INDETERMINATE = "indeterminate"
NOT_EVALUABLE = "not_evaluable"

VALID_VERDICTS = {
    VARIATION,
    COLLAPSE,
    INDETERMINATE,
    NOT_EVALUABLE,
}


def classify_within_form_stratum(
    signatures,
):
    """
    Classify one fine-form stratum.

    Each element represents one analysis unit.

    A canonical signature string means the observation is evaluable.
    None means the observation is non-evaluable under the frozen
    canonical packaging schema.

    Rules
    -----
    VARIATION
        At least two distinct evaluable canonical signatures occur.

        Missing observations cannot erase an observed variation result.

    COLLAPSE
        Exactly one distinct canonical signature occurs AND every
        observation is evaluable.

    INDETERMINATE
        Exactly one distinct canonical signature is observed, but at
        least one observation is non-evaluable.

        Therefore absence of variation cannot be established.

    NOT_EVALUABLE
        No observation has an evaluable canonical signature.
    """

    values = list(signatures)

    if not values:
        return {
            "verdict": NOT_EVALUABLE,
            "n_total": 0,
            "n_evaluable": 0,
            "n_non_evaluable": 0,
            "n_distinct_signatures": 0,
            "signatures": (),
        }

    evaluable = [
        x
        for x in values
        if x is not None
    ]

    distinct = tuple(
        sorted(set(evaluable))
    )

    n_total = len(values)
    n_evaluable = len(evaluable)
    n_non_evaluable = (
        n_total - n_evaluable
    )

    if len(distinct) >= 2:
        verdict = VARIATION

    elif len(distinct) == 1:

        if n_non_evaluable == 0:
            verdict = COLLAPSE

        else:
            verdict = INDETERMINATE

    else:
        verdict = NOT_EVALUABLE

    return {
        "verdict": verdict,
        "n_total": n_total,
        "n_evaluable": n_evaluable,
        "n_non_evaluable": n_non_evaluable,
        "n_distinct_signatures": len(distinct),
        "signatures": distinct,
    }


def primary_family_summary(
    strata,
):
    """
    Summarize fine-form-stratum verdicts WITHOUT pooling signatures.

    `strata` maps:
        fine_form -> iterable[signature | None]

    This function reports stratum-level outcomes only.

    It deliberately does not calculate a pooled family signature
    richness because that quantity is architecture/form-confounded.
    """

    result = {}

    for form in sorted(strata):
        result[form] = (
            classify_within_form_stratum(
                strata[form]
            )
        )

    counts = {
        VARIATION: 0,
        COLLAPSE: 0,
        INDETERMINATE: 0,
        NOT_EVALUABLE: 0,
    }

    for row in result.values():
        counts[row["verdict"]] += 1

    return {
        "strata": result,
        "verdict_counts": counts,
        "n_strata": len(result),
    }


def common_k(
    stratum_sizes_a,
    stratum_sizes_b,
):
    """
    Return the largest common sampling depth supported by every
    INCLUDED stratum in two comparison sets.

    This helper only defines the mechanical common-k limit.

    It does NOT authorize pooling across pharmaceutical forms and
    does NOT itself perform rarefaction.
    """

    sizes = [
        int(x)
        for x in (
            list(stratum_sizes_a)
            + list(stratum_sizes_b)
        )
        if int(x) > 0
    ]

    if not sizes:
        return 0

    return min(sizes)
