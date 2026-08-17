# Parenteral PPI Evidence Milestone — 2026-08-17

## Scope

This milestone freezes the first evidence collection and first hold-resolution
assessment for the 46-licence parenteral proton-pump-inhibitor universe.

The processed evidence files remain intentionally untracked under the repository
policy defined by:

    data/processed/*

Only their deterministic state and SHA256 identifiers are recorded here.

## Evidence universe

- Total licences: 46
- Main evidence CONFIRMED: 39
- Main evidence UNKNOWN: 7
- Actionable unresolved after first sweep: 0
- Frozen initial hold registry: 8 licences
- First hold-resolution assessments completed: 8 / 8

Important:

`PENDING = 0` in the resolution queue does not mean that all eight initial
holds were resolved to confirmed packaging evidence. It means that every hold
received a first explicit resolution assessment.

Only JECTOSEM 2017/495 was fully promoted from UNKNOWN to CONFIRMED during
this resolution pass.

## Hold-resolution status distribution

- RESOLVED_CONFIRMED: 1
- LEGACY_KUB_IDENTIFIED_CURRENT_KUB_PENDING: 1
- OFFICIAL_KUB_FOUND_LICENCE_LINK_PENDING: 1
- KT_PACKAGING_CONFIRMED_KUB_PENDING: 1
- KUB_EXISTENCE_CONFIRMED_TEXT_PENDING: 1
- PRODUCT_ID_CONFIRMED_KUB_DOCUMENT_PENDING: 2
- OFFICIAL_TITCK_IV_RECORD_CONFIRMED_KUB_PENDING: 1
- PENDING: 0

Total resolution queue rows: 8.

## Fully resolved hold

### JECTOSEM — licence 2017/495

The product-holder-licence-KUB chain was explicitly established.

Observed KUB 6.5 packaging evidence:

- vial: Type I colourless glass
- stopper: bromobutyl
- closure: aluminium or plastic flip-off cap
- packaged solvent: none

The source wording "aluminium or plastic" is preserved as an alternative and
is not collapsed into a single material.

## Remaining seven UNKNOWN main-evidence licences

These records received explicit resolution assessments but were not promoted
to CONFIRMED because the project's evidence threshold was not met.

- PROTAZ — 2016/873
- PULCET — 2018/364
- ENPRO — 2018/706
- PASMOL — 2020/252
- JECTOPAN — 2024/239
- REFLOSEL — 2024/563
- OMHEAL — 2025/605

No missing vial, stopper, closure, solvent, manufacturing-site, or other
component evidence was inferred from peer products.

## Processed artefact hashes

### Main evidence workbook

Path:

    data/processed/parenteral_ppi_evidence_2026_08_17.xlsx

SHA256:

    59D3C4A4056E9F83939528DC85EECA103346A2E84016D2D0F98F378F431D0130

### Frozen initial hold registry

Path:

    data/processed/parenteral_ppi_evidence_holds_2026_08_17.csv

SHA256:

    02EBC793473F72AC9BBCD36EB797DBF7C423738DE0C888172324C58BCEB3ABBD

This file is the frozen snapshot of the eight holds produced by the initial
evidence sweep and was not modified during resolution work.

### Hold-resolution queue

Path:

    data/processed/parenteral_ppi_hold_resolution_queue_2026_08_17.csv

SHA256:

    7B438C1F652B2FE4046164A519731B09166F3A181A8152E27715A1300AEFE395

## Integrity rules preserved

1. Missing evidence was not converted into positive evidence.
2. Packaging/component attributes were not transferred from peer products.
3. KT evidence was not promoted to KUB 6.5 evidence.
4. Product identity or KUB existence alone was not treated as observed
   packaging evidence.
5. Licence-level linkage was required where relevant.
6. Source conflicts and unresolved document-linkage states were preserved.
7. `URETICI` and `URETIM_YERI` remained UNKNOWN unless explicitly evidenced.
8. The frozen eight-hold registry remained byte-identical throughout the
   resolution pass.

## Test state

Current working-tree full test suite:

    93 passed

Interpretation:

- previous committed-baseline verified result: 87 passed
- additional untracked `tests/test_gate_a.py` tests: 6
- therefore current 93-test result includes work from the separate Gate-A /
  product-universe workstream and must not be interpreted as 93 tests belonging
  solely to this evidence milestone.

## Git policy

Processed evidence artefacts are intentionally excluded from Git by the
repository's existing `data/processed/*` ignore rule.

They must not be force-added merely to freeze this milestone. Reproducibility
and provenance are instead preserved through:

- source/raw inputs,
- deterministic code,
- explicit audit documentation,
- frozen SHA256 identifiers,
- and Git history.

## Milestone state

Parenteral PPI first evidence sweep:

    COMPLETE

Eight-hold first resolution assessment:

    COMPLETE

Main evidence state:

    39 CONFIRMED + 7 UNKNOWN

Next work should treat the seven UNKNOWN records as explicit evidence gaps,
not as unreviewed records.
