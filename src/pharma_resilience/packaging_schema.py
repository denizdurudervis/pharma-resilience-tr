"""
Frozen structural representation for Stage-2 packaging evidence.

IMPORTANT
---------
This schema represents documented immediate-pack architecture at a
declared canonical resolution.

It does NOT establish:
- supplier identity,
- component manufacturer identity,
- supply independence,
- common failure modes,
- redundancy,
- resilience.

Applicability is architecture-derived.
Coders cannot assign NOT_APPLICABLE row by row.

Primary inference is performed within fine pharmaceutical-form strata.
Raw signature richness must not be pooled across architectures or
compared directly between Stage-2 arms.
"""

from dataclasses import dataclass, field
from typing import Mapping


OBSERVED = "OBSERVED"
NOT_STATED = "NOT_STATED"
UNMAPPED_REVIEW = "UNMAPPED_REVIEW"
UNKNOWN = "UNKNOWN"

VALID_STATES = {
    OBSERVED,
    NOT_STATED,
    UNMAPPED_REVIEW,
    UNKNOWN,
}

NON_EVALUABLE_STATES = {
    NOT_STATED,
    UNMAPPED_REVIEW,
    UNKNOWN,
}


# Frozen architecture -> applicability map.
#
# primary_pack_family is applicable to every architecture.
#
# closure_barrier_family is applicable only where an immediate
# closure/barrier is structurally distinct from the primary pack.
#
# Structural non-applicability is derived from this map. It is never
# entered manually as an evidence state.
ARCHITECTURE_RULES = {
    "blister": {
        "closure_barrier_applicable": True,
    },
    "bottle": {
        "closure_barrier_applicable": True,
    },
    "vial_closure": {
        "closure_barrier_applicable": True,
    },
    "prefilled_syringe": {
        "closure_barrier_applicable": True,
    },
    "cartridge_device": {
        "closure_barrier_applicable": True,
    },
    "bag_port": {
        "closure_barrier_applicable": True,
    },
    "tube": {
        "closure_barrier_applicable": True,
    },

    # Integral-seal systems
    "ampoule": {
        "closure_barrier_applicable": False,
    },
    "sachet": {
        "closure_barrier_applicable": False,
    },
    "strip_pack": {
        "closure_barrier_applicable": False,
    },
}


@dataclass(frozen=True)
class CanonicalField:
    """
    One source-supported canonical field.

    OBSERVED
        A canonical family value is supported by source evidence.

    NOT_STATED
        The field is applicable, but the source does not state it.

    UNMAPPED_REVIEW
        Source wording exists, but no frozen mapping currently exists.

    UNKNOWN
        Wording has been reviewed, but identity cannot be resolved.

    Structural non-applicability is NOT an evidence state.
    It is derived from architecture.
    """

    state: str
    value: str = ""

    def __post_init__(self):

        if self.state not in VALID_STATES:
            raise ValueError(
                f"Invalid evidence state: {self.state!r}"
            )

        value = str(
            self.value or ""
        ).strip()

        if (
            self.state == OBSERVED
            and not value
        ):
            raise ValueError(
                "OBSERVED fields require a value."
            )

        if (
            self.state != OBSERVED
            and value
        ):
            raise ValueError(
                f"{self.state} cannot carry "
                "a canonical value."
            )

        object.__setattr__(
            self,
            "value",
            value,
        )

    @property
    def evaluable(self):
        return self.state == OBSERVED


@dataclass(frozen=True)
class PackagingObservation:
    """
    One Stage-2 documented immediate-pack observation.

    Primary core dimensions:

        architecture
        primary_pack_family
        closure_barrier_family
            only where architecture says the slot applies

    device_or_copack and optional_attributes are secondary layers
    and do not affect the primary core signature.
    """

    product_id: str
    source_reference: str
    verbatim_text: str

    architecture: CanonicalField
    primary_pack_family: CanonicalField

    closure_barrier_family: (
        CanonicalField | None
    ) = None

    device_or_copack: (
        CanonicalField | None
    ) = None

    optional_attributes: Mapping[str, str] = field(
        default_factory=dict
    )

    def __post_init__(self):

        product_id = str(
            self.product_id or ""
        ).strip()

        source_reference = str(
            self.source_reference or ""
        ).strip()

        verbatim_text = str(
            self.verbatim_text or ""
        ).strip()

        if not product_id:
            raise ValueError(
                "product_id is required."
            )

        if not source_reference:
            raise ValueError(
                "source_reference is required."
            )

        object.__setattr__(
            self,
            "product_id",
            product_id,
        )

        object.__setattr__(
            self,
            "source_reference",
            source_reference,
        )

        object.__setattr__(
            self,
            "verbatim_text",
            verbatim_text,
        )

        # Applicability can only be enforced when architecture
        # itself has been canonically resolved.
        if self.architecture.state != OBSERVED:
            return

        architecture = self.architecture.value

        if architecture not in ARCHITECTURE_RULES:
            raise ValueError(
                "Observed architecture is not in the "
                f"frozen vocabulary: {architecture!r}"
            )

        closure_applies = (
            ARCHITECTURE_RULES[
                architecture
            ][
                "closure_barrier_applicable"
            ]
        )

        if (
            closure_applies
            and self.closure_barrier_family
            is None
        ):
            raise ValueError(
                "This architecture requires a "
                "closure_barrier_family field. "
                "Use NOT_STATED, UNKNOWN or "
                "UNMAPPED_REVIEW if unresolved."
            )

        if (
            not closure_applies
            and self.closure_barrier_family
            is not None
        ):
            raise ValueError(
                "closure_barrier_family is structurally "
                "non-applicable for this architecture "
                "and must be None."
            )


def architecture_resolved(observation):
    return (
        observation.architecture.state
        == OBSERVED
        and observation.architecture.value
        in ARCHITECTURE_RULES
    )


def applicable_core_fields(observation):
    """
    Return the core fields structurally applicable to this
    architecture.

    Applicability is deterministic and cannot be set row by row.
    """

    if not architecture_resolved(observation):
        return ()

    architecture = (
        observation.architecture.value
    )

    fields = [
        "architecture",
        "primary_pack_family",
    ]

    if (
        ARCHITECTURE_RULES[
            architecture
        ][
            "closure_barrier_applicable"
        ]
    ):
        fields.append(
            "closure_barrier_family"
        )

    return tuple(fields)


def core_signature(observation):
    """
    Primary canonical signature.

    Returns None if any APPLICABLE core field is unresolved.

    Structurally non-applicable slots are omitted rather than encoded
    as artificial signature levels.
    """

    if not architecture_resolved(
        observation
    ):
        return None

    architecture = (
        observation.architecture.value
    )

    if (
        observation.primary_pack_family.state
        != OBSERVED
    ):
        return None

    tokens = [
        f"architecture={architecture}",
        (
            "primary_pack_family="
            + observation.primary_pack_family.value
        ),
    ]

    closure_applies = (
        ARCHITECTURE_RULES[
            architecture
        ][
            "closure_barrier_applicable"
        ]
    )

    if closure_applies:

        closure = (
            observation.closure_barrier_family
        )

        if (
            closure is None
            or closure.state != OBSERVED
        ):
            return None

        tokens.append(
            "closure_barrier_family="
            + closure.value
        )

    return "|".join(tokens)


def core_evaluable(observation):
    return (
        core_signature(observation)
        is not None
    )


def non_evaluable_reasons(observation):
    """
    Return only APPLICABLE unresolved core fields.
    """

    reasons = []

    if (
        observation.architecture.state
        != OBSERVED
    ):
        reasons.append(
            (
                "architecture",
                observation.architecture.state,
            )
        )

        return tuple(reasons)

    architecture = (
        observation.architecture.value
    )

    if architecture not in ARCHITECTURE_RULES:
        reasons.append(
            (
                "architecture",
                "UNMAPPED_ARCHITECTURE",
            )
        )

        return tuple(reasons)

    if (
        observation.primary_pack_family.state
        != OBSERVED
    ):
        reasons.append(
            (
                "primary_pack_family",
                observation.primary_pack_family.state,
            )
        )

    if (
        ARCHITECTURE_RULES[
            architecture
        ][
            "closure_barrier_applicable"
        ]
    ):

        closure = (
            observation.closure_barrier_family
        )

        if closure is None:
            reasons.append(
                (
                    "closure_barrier_family",
                    "FIELD_MISSING",
                )
            )

        elif closure.state != OBSERVED:
            reasons.append(
                (
                    "closure_barrier_family",
                    closure.state,
                )
            )

    return tuple(reasons)


def specific_signature(observation):
    """
    Sensitivity-only representation.

    Primary core signature is preserved.

    Observed device/co-pack information and explicitly supported
    optional attributes are appended, but never alter the primary
    core result.
    """

    core = core_signature(
        observation
    )

    if core is None:
        return None

    details = []

    device = observation.device_or_copack

    if (
        device is not None
        and device.state == OBSERVED
    ):
        details.append(
            "device_or_copack="
            + device.value
        )

    for key, value in sorted(
        observation.optional_attributes.items()
    ):
        key = str(
            key or ""
        ).strip()

        value = str(
            value or ""
        ).strip()

        if key and value:
            details.append(
                f"{key}={value}"
            )

    if not details:
        return core

    return (
        core
        + "|"
        + "|".join(details)
    )
