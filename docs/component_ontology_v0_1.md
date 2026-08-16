# Pharmaceutical Packaging Component Ontology v0.1

Frozen before product-level component extraction.

## Purpose

This ontology defines the physical packaging and presentation
components that may be extracted from public KÜB/KT documentation
for the frozen pharmaceutical audit sample.

The ontology is defined before component-level convergence analysis
to avoid creating categories in response to observed network results.

## Evidence semantics

A component recorded from a public product document represents an
observed component of the authorised product presentation.

It does NOT by itself establish:

- a unique supplier;
- a unique manufacturing origin;
- a unique approved component specification;
- inability to substitute an alternative component;
- mandatory dependence on a particular supplier or facility;
- a common-mode failure point.

Therefore:

observed presentation component
!= supplier dependency
!= non-substitutable dependency
!= proven failure mode

## Resolution levels

### R0 — process class

Examples:

- liquid
- lyophilized

### R1 — primary container class

Examples:

- ampoule
- vial
- prefilled syringe
- bottle
- bag

### R2 — container material / specification class

Examples:

- Type I glass vial
- Type I glass ampoule
- plastic container
- HDPE bottle

Only record material/specification information when explicitly
supported by the source document.

### R3 — closure / sealing component class

Examples:

- rubber stopper
- bromobutyl rubber stopper
- chlorobutyl rubber stopper
- aluminium cap
- flip-off seal

Do not infer elastomer composition when the source states only
"rubber stopper".

### R4 — co-packaged administration or reconstitution component

Examples:

- solvent ampoule
- solvent vial
- diluent syringe
- administration device

The pharmaceutical product and the co-packaged component must remain
distinguishable in the data model.

### R5 — secondary / printed packaging

Examples:

- carton
- label
- package leaflet

Record only when explicitly documented and relevant to the analysis.

## Component roles

Allowed component-role values:

- primary_container
- closure
- seal
- solvent_container
- diluent_component
- administration_device
- secondary_package
- printed_material
- other_explicit_component

## Observation status

Allowed values:

- explicit
- absent
- unresolved

`explicit`:
The component is explicitly described in the cited public document.

`absent`:
The audited document explicitly establishes that the component is not
part of the presentation or the field is not applicable.

`unresolved`:
The available public documentation does not support a reliable
component-level classification.

Missing information must not be converted to absence.

## Granularity rule

Always preserve both:

1. the raw source wording; and
2. the normalized component class.

Example:

raw:
"Type I colourless glass vial closed with bromobutyl rubber stopper
and aluminium flip-off cap"

normalized nodes:

- primary_container::type_I_clear_glass_vial
- closure::bromobutyl_rubber_stopper
- seal::aluminium_flip_off_cap

## Conservative normalization

Normalize two observations to the same component node only when the
public wording supports equivalence at the selected resolution.

Do not merge:

- rubber stopper
- bromobutyl rubber stopper

at the highest material-specific resolution.

They may share a broader parent class:

closure::rubber_stopper

while remaining distinct at the child level.

## Hierarchical representation

Where evidence permits, a component may have both a broad and a
specific representation.

Example:

closure::rubber_stopper
    -> closure::bromobutyl_rubber_stopper

This enables granularity-sensitivity analysis without destroying the
original evidence.

## Analytical rule

Cross-product or cross-ingredient convergence at a component node is
descriptive.

A shared component class may indicate a potential common dependency
channel, but direct disruption/interdiction analysis requires
additional evidence regarding supplier, origin, facility,
substitutability, or approved alternatives.

## Provenance requirement

Every explicit component observation must retain:

- product_id
- source document identifier
- document type
- document date/version when available
- section
- raw source wording
- normalized component role
- normalized component class
- evidence status
- notes

No component node may be introduced solely from model expectation or
industry convention when the product document does not support it.