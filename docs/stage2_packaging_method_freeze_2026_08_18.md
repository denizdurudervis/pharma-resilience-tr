# Stage-2 Packaging Method Freeze

**Freeze date:** 2026-08-18  
**Project:** Pharma-Resilience-TR  
**Status:** Frozen before substantive Stage-2 K?B packaging coding

---

## 1. Purpose

This document freezes the Stage-2 packaging representation,
primary inference rules, and blinded canonicalisation protocol.

The selected Stage-2 family roles were frozen previously:

- `FAM_SGLT2` ? homogeneous falsification arm
- `FAM_BISPHOSPHONATE` ? heterogeneous stress-test arm

No family replacement will be made merely because a later
Stage-2 result is null, negative, ambiguous, or inconvenient.

---

## 2. What the packaging representation measures

The Stage-2 packaging representation measures:

> documented immediate-pack architecture at a declared
> canonical resolution in public product documentation.

It does NOT establish:

- supplier identity
- component manufacturer identity
- supply independence
- common failure mode
- redundancy
- false redundancy
- resilience

Those claims require additional evidence.

---

## 3. Architecture-aware schema

The implementation is:

`src/pharma_resilience/packaging_schema.py`

Primary representation uses:

1. architecture
2. primary_pack_family
3. closure_barrier_family, only where structurally applicable

Structural applicability is determined by the frozen
architecture rule table.

It is not a row-level coder decision.

`NOT_APPLICABLE` is therefore not an evidence state and is not
inserted into signatures as a token.

Evidence states are:

- `OBSERVED`
- `NOT_STATED`
- `UNMAPPED_REVIEW`
- `UNKNOWN`

An applicable unresolved core field makes the primary canonical
signature non-evaluable.

Structurally non-applicable fields are omitted.

---

## 4. Core versus secondary information

Primary core information represents documented immediate-pack
architecture/component-family identity at the declared canonical
resolution.

Details that refine, but do not replace, the immediate-pack family
identity remain secondary.

Examples include, where applicable:

- colour
- nominal volume
- detailed stopper geometry
- detailed cap geometry
- grade/subgrade
- coating descriptors
- administration-device details
- co-pack details

Secondary attributes may be used for sensitivity analysis.

They do not modify the primary canonical verdict.

Movement of a variable between primary and secondary layers after
unblinding is prohibited for the frozen primary analysis.

Any later alternative resolution must be explicitly labelled as a
sensitivity analysis.

---

## 5. Primary unit of inference

Primary inference is strictly within fine pharmaceutical-form strata.

Canonical signatures are not pooled across fine forms for the
primary result.

Raw distinct-signature counts are not compared directly between
Stage-2 arms.

This avoids mechanically favouring families with more packaging
architectures or more structurally applicable fields.

Implementation:

`src/pharma_resilience/stage2_inference.py`

---

## 6. Frozen within-form verdicts

For one fine pharmaceutical-form stratum:

### VARIATION

At least two distinct evaluable canonical core signatures are
observed.

Missing observations cannot erase directly observed variation.

### COLLAPSE

Exactly one distinct canonical core signature is observed AND
every relevant analysis unit is evaluable.

### INDETERMINATE

Exactly one canonical core signature is observed, but at least
one relevant unit is non-evaluable.

Absence of variation therefore cannot be established.

### NOT_EVALUABLE

No unit in the stratum has an evaluable canonical core signature.

These definitions must not be changed after Stage-2 outcomes are
known.

---

## 7. Missingness reporting

Missingness will always be reported:

- by Stage-2 arm
- by fine pharmaceutical-form stratum
- by applicable core field
- as evaluable versus non-evaluable analysis units

Complete-case proportions are descriptive diagnostics.

A low-completeness stratum cannot be called COLLAPSE unless every
relevant unit is evaluable under the frozen primary schema.

---

## 8. Cross-arm comparisons

Primary inference does NOT compare raw packaging-signature richness
between the two Stage-2 families.

If a quantitative cross-arm diversity comparison is performed later,
it is secondary.

Such a comparison must:

- operate within comparable fine-form strata;
- use a common sampling depth `k`;
- use rarefaction/resampling rather than raw richness;
- report the eligible strata and common `k`;
- remain separate from the primary within-form verdicts.

---

## 9. Canonical versus verbatim resolution

Primary result:

- canonical core packaging representation

Sensitivity result:

- verbatim source wording
- optional/specific canonical attributes

If verbatim and canonical conclusions differ, that discrepancy is
reported as resolution sensitivity.

It is not discarded as noise.

---

## 10. Blinded two-pass canonicalisation protocol

Canonical terminology must not be assigned while the coder is using
family identity or Stage-2 arm identity to interpret the desired
result.

### Pass 1 ? verbatim evidence extraction

For every eligible Stage-2 analysis unit:

- retain the source reference;
- retain the exact relevant packaging wording;
- retain sufficient provenance to reconnect later;
- do not infer supply independence;
- do not collapse wording into final canonical categories during
  extraction.

A private linkage key may retain product identity for later
reconnection.

### Pass 2 ? blinded term pool

Create a pooled list of distinct verbatim packaging terms.

Before canonical mapping, remove or replace, where operationally
possible:

- product name
- family identifier
- Stage-2 role
- MAH identity
- ordering that reveals family blocks

Each blinded term receives a neutral term identifier.

Canonical mapping is performed against this blinded term pool.

### Pass 3 ? vocabulary freeze

The mapping table must contain at least:

- blind_term_id
- verbatim_term
- canonical_field
- canonical_value
- mapping_state
- mapping_note
- mapping_version

Permitted mapping states include:

- `MAPPED`
- `NOT_STATED`
- `UNKNOWN`
- `UNMAPPED_REVIEW`

Before unblinding:

1. save the complete mapping table;
2. compute a cryptographic hash;
3. record the mapping version;
4. commit the mapping rules/version metadata.

Only after that freeze may product/family identities be reattached
for the primary analysis.

---

## 11. Unseen-term update protocol

New terminology may occur after the first mapping freeze.

It must never be silently forced into an existing category.

An unseen term is initially:

`UNMAPPED_REVIEW`

A mapping update must:

1. preserve the original term;
2. document the reason for the mapping;
3. increment the mapping version;
4. recompute and record the mapping-file hash;
5. rerun the complete Stage-2 analysis;
6. compare primary verdicts across mapping versions.

If a Stage-2 primary verdict changes solely because the canonical
mapping version changed, that instability must be reported.

No earlier mapping version is deleted.

---

## 12. Prohibited outcome-driven actions

After unblinding, the following are prohibited for the frozen primary
analysis:

- replacing SGLT2 or BISPHOSPHONATE because of their results;
- moving an attribute from secondary to core to create or remove
  variation;
- moving a core attribute to secondary to create collapse;
- changing architecture applicability row by row;
- treating missing documentation as a new component category;
- pooling fine pharmaceutical-form strata to increase apparent
  diversity;
- reporting only the mapping version with the preferred verdict;
- silently excluding non-evaluable products;
- interpreting canonical equality as supplier equality.

---

## 13. Publication commitment

All primary Stage-2 outcomes are reportable, including:

- variation
- collapse
- indeterminate
- not_evaluable
- resolution-sensitive results
- mapping-version instability
- systematic documentation missingness

A null or non-evaluable result will not be replaced by another family.

---

## 14. Current implementation checkpoint

At the time this protocol was written:

Packaging schema tests passed.

Stage-2 inference tests passed.

Combined packaging/inference tests passed.

Full repository suite:

`157 passed`

The schema and inference implementation remain subject to this
method freeze and will be committed together with this document
before substantive Stage-2 K?B canonical coding begins.
