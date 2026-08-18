"""
Prospectively frozen Stage-2 family-role selection logic.

The rules use Stage-1 variables only and must be applied before
inspection of Stage-2 K?B / packaging-component evidence.

Role A:
    Homogeneous falsification arm.
    Among families with exactly one known fine pharmaceutical form
    and zero unknown-form licences, select the family with the
    largest active-licence count.

Role B:
    Heterogeneous stress-test arm.
    Among families represented by at least two coarse systems,
    select the family with the largest coarse effective-system
    number.

Tie-breaking uses larger active N, then lexical family_id.
"""


def select_stage2_roles(metrics):
    rows = [dict(x) for x in metrics]

    homogeneous = [
        r
        for r in rows
        if (
            int(r["fine_forms"]) == 1
            and int(r["unknown"]) == 0
        )
    ]

    if not homogeneous:
        raise ValueError(
            "No strict single-fine-form family available."
        )

    homogeneous.sort(
        key=lambda r: (
            -int(r["n"]),
            str(r["family"]),
        )
    )

    role_a = homogeneous[0]

    heterogeneous = [
        r
        for r in rows
        if (
            int(r["coarse_systems"]) >= 2
            and str(r["family"])
            != str(role_a["family"])
        )
    ]

    if not heterogeneous:
        raise ValueError(
            "No heterogeneous family available."
        )

    heterogeneous.sort(
        key=lambda r: (
            -float(r["coarse_eff"]),
            -int(r["n"]),
            str(r["family"]),
        )
    )

    role_b = heterogeneous[0]

    return {
        "homogeneous_falsification": role_a,
        "heterogeneous_stress_test": role_b,
    }
