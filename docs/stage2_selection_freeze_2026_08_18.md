# Stage-2 Family Selection Freeze

**Freeze date:** 2026-08-18  
**Project:** Pharma-Resilience-TR  
**Status:** Prospective freeze for Stage-2 packaging/component evidence collection

## 1. Scope of this freeze

Stage-1 exploratory screening has been completed using the active
T?TCK licence universe and pharmaceutical-form information.

This freeze is made **before inspection or collection of new Stage-2
K?B 6.5 packaging/component evidence for the selected families**.

The overall project is therefore not described as preregistered.

The correct interpretation is:

> Stage-1 was exploratory. Stage-2 family-role selection and the
> corresponding decision rules were prospectively frozen before
> Stage-2 packaging evidence inspection.

## 2. Frozen Stage-1 analysis universe

The Stage-1 pipeline produced:

- 2,412 ATC-consistent source presentations
- 1,436 non-empty distinct licences
- 1,372 ALL_ACTIVE licences
- 64 ALL_SUSPENDED licences
- 0 MIXED licences
- 0 UNKNOWN_STATUS licences
- 14 clinical families
- 7 active licences with conservatively unresolved pharmaceutical form

Pharmaceutical-form classification and licence-level reconciliation
were frozen before Stage-2 family selection.

## 3. Resolution-sensitivity principle

Two descriptive resolutions were used in Stage-1:

1. **Fine pharmaceutical form**
2. **Coarse administration / route-system class**

The coarse taxonomy is defined in:

`src/pharma_resilience/route_system.py`

These classes are descriptive administration-system groupings.

They are **not** interpreted as independent supply routes,
independent manufacturing chains, or independent sources of supply.

## 4. Stage-2 roles

Stage-2 uses two families with deliberately different roles.

### Role A ? homogeneous falsification arm

**Selected family:** `FAM_SGLT2`

Selection rule:

> Among families with exactly one known fine pharmaceutical form
> and zero unknown-form licences, select the family with the largest
> active-licence count.

Observed Stage-1 values:

- active licences: 48
- unknown-form licences: 0
- fine pharmaceutical forms: 1
- largest fine-form stratum: 48
- coarse systems: 1

Rationale:

The pharmaceutical-form dimension is held constant within this family.
Therefore, any reproducible canonical packaging/component variation
observed inside the family cannot be attributed merely to variation
between pharmaceutical-form classes.

This arm is intended as a falsification-oriented test of the hypothesis
that packaging/component variation is primarily explained by
pharmaceutical form.

### Role B ? heterogeneous stress-test arm

**Selected family:** `FAM_BISPHOSPHONATE`

Selection rule:

> Among families represented by at least two coarse route systems,
> select the family with the highest inverse-Simpson effective number
> of coarse systems.

Observed Stage-1 values:

- active licences: 90
- unknown-form licences: 2
- fine pharmaceutical forms: 8
- coarse systems: 4
- coarse effective-system number: 2.764
- largest fine-form stratum: 25
- second-largest fine-form stratum: 23

Rationale:

This family represents the opposite Stage-1 structural extreme:
substantial administration-system heterogeneity remains even after
coarsening pharmaceutical-form terminology.

It is therefore used as a stress-test arm rather than as an assumed
positive example of supply diversity.

## 5. Deterministic implementation

The frozen selection logic is implemented in:

`src/pharma_resilience/stage2_selection.py`

The associated tests are in:

`tests/test_stage2_selection.py`

At the time of this freeze:

- Stage-2 selection tests: 6 passed
- full repository test suite: 133 passed

Git checkpoint immediately preceding this document:

`b59230d` ? freeze deterministic Stage-2 family selection logic

## 6. Claims explicitly NOT made from Stage-1

Stage-1 pharmaceutical-form or route-system diversity does not establish:

- supply-route independence
- packaging-component independence
- manufacturing-site independence
- supplier independence
- product availability or actual marketing status
- utilisation or market share
- resilience
- redundancy
- false redundancy

Stage-1 counts are licence-level structural descriptors only.

## 7. Stage-2 outcome commitment

Both selected families will be retained regardless of Stage-2 result.

The family set will not be changed merely because packaging evidence
produces an undesirable, null, negative, ambiguous, or non-evaluable
result.

The following outcomes are all reportable:

- canonical within-form component variation
- canonical component collapse
- resolution-sensitive variation
- missingness-driven ambiguity
- insufficient comparable documentation
- not_evaluable

A negative result will not be silently replaced by another family.

## 8. Packaging vocabulary rule

Before substantive Stage-2 inference, a canonical packaging/component
coding schema will be frozen.

The schema must:

- distinguish verbatim source wording from canonical coding;
- preserve missingness rather than convert missing information into
  artificial component variation;
- avoid inferring material or component identity when not supported
  by the source;
- include an explicit `UNMAPPED_REVIEW` state for unseen terminology;
- prevent silent creation of new outcome-driven categories;
- preserve enough source evidence for later audit.

The canonical schema will be reviewed before applying it at scale.

## 9. Primary Stage-2 question

The Stage-2 comparison asks:

> After controlling for pharmaceutical-form structure, does canonical
> packaging/component variation remain, and does its behaviour differ
> between a strictly form-homogeneous family and a route-system-
> heterogeneous family?

This question concerns observable public-document structure.

Any later claim concerning supply redundancy or false redundancy will
require additional evidence beyond pharmaceutical-form and packaging
description alone.
