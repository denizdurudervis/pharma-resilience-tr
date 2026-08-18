"""
Deterministic coarse administration-system taxonomy.

This layer is intentionally coarser than pharmaceutical_form.
It is used for Stage-1 resolution-sensitivity analysis and
Stage-2 family selection only.

It must not be interpreted as supply-route independence.
"""

ROUTE_SYSTEM_BY_FORM = {
    # Oral solids
    "tablet": "oral_solid",
    "film_coated_tablet": "oral_solid",
    "enteric_coated_tablet": "oral_solid",
    "modified_release_tablet": "oral_solid",
    "effervescent_tablet": "oral_solid",
    "orodispersible_tablet": "oral_solid",
    "dragee": "oral_solid",
    "capsule": "oral_solid",

    # Oromucosal
    "sublingual_tablet": "oromucosal_solid",

    # Oral liquids
    "syrup": "oral_liquid",
    "oral_solution": "oral_liquid",
    "oral_suspension": "oral_liquid",
    "oral_drops": "oral_liquid",

    # Route not safely inferable from generic wording
    "drops": "unspecified_liquid",
    "suspension": "unspecified_liquid",

    # Parenteral
    "injection_solution": "parenteral_solution",
    "infusion_solution": "parenteral_solution",
    "injection_concentrate": "parenteral_concentrate",
    "infusion_concentrate": "parenteral_concentrate",
    "injection_suspension": "parenteral_suspension",
    "lyophilized_powder": "parenteral_lyophilized",

    # Rectal
    "rectal_solution": "rectal",
    "rectal_tube": "rectal",
    "suppository": "rectal",

    # Other
    "nasal_spray": "nasal",
    "oral_spray": "oral_spray",
    "transdermal_patch": "transdermal",

    # Explicit missingness
    "unknown_form": "unknown_system",
}


def coarsen_pharmaceutical_form(form):
    """
    Map one canonical pharmaceutical form to the frozen
    Stage-1 coarse administration-system taxonomy.

    Unknown vocabulary is never silently guessed.
    """
    key = str(form or "").strip()

    if key not in ROUTE_SYSTEM_BY_FORM:
        raise KeyError(
            f"Unmapped pharmaceutical form: {key!r}"
        )

    return ROUTE_SYSTEM_BY_FORM[key]


def effective_number_from_counts(counts):
    """
    Inverse-Simpson effective number.

    counts may be any iterable of non-negative counts.
    """
    values = [
        int(x)
        for x in counts
        if int(x) > 0
    ]

    total = sum(values)

    if total == 0:
        return 0.0

    hhi = sum(
        (x / total) ** 2
        for x in values
    )

    return 1.0 / hhi
