# TİTCK Licensed-Product Universe Rules v0.1

## Status

Pre-specified before expanded-sample product matching and before any
packaging/component extraction.

## Frozen source snapshot

Source:
TİTCK Ruhsatlı Beşeri Tıbbi Ürünler Listesi

Snapshot date:
2026-08-14

Local frozen filename:
data/raw/titck_licensed_products_2026_08_14.xlsx

SHA-256:
8F3181DC2DC636C08135094C5B30BD9CB1FD8B2BF66D414C18F12178289D2D68

Only the main licensed-human-medicinal-product worksheet is used for the
primary expanded product universe.

No packaging information is used during product-universe construction.

---

# 1. Product-unit definition

The primary analytical product unit is the marketing-authorisation/licence,
identified by RUHSAT NUMARASI.

Multiple barcodes or package presentations associated with the same licence
are retained as presentation metadata but do not automatically count as
independent medicinal products.

This rule limits pseudo-replication caused by multiple pack sizes of the same
licensed medicinal product.

---

# 2. Licence-status rule

The primary eligible product universe contains products with non-suspended
licence status in the frozen TİTCK snapshot.

Suspended records are retained in the audit output but are not counted toward
the primary eligible-product threshold.

Mixed suspension states within the same licence are flagged for manual review.

---

# 3. Active-ingredient rule

A product is assigned to a candidate active ingredient only when the TİTCK
ETKİN MADDE field supports a deterministic match to the pre-specified seed.

Accepted normalisation includes:

- Turkish/English spelling variants;
- salt forms;
- hydrate forms;
- common source spelling variants.

The original TİTCK wording is always preserved.

Canonicalisation does not itself establish clinical equivalence.

---

# 4. Monotherapy restriction

The primary expanded sample is restricted to single-active-ingredient
products.

Combination products are excluded from the primary product universe because
their clinical comparison and component topology may be driven by an
additional active ingredient.

Examples of combination markers include:

- +
- /
- comma-separated multiple actives
- "ve"
- "and"

Combination products are retained in the audit output with an exclusion flag.

They are not silently discarded.

---

# 5. ATC consistency rule

Active-ingredient matching must also be consistent with the pre-specified
family ATC scope.

ATC is used as a consistency filter, not as the sole ingredient-identification
method.

A row with:

- a seed-ingredient match but unexpected ATC;
- missing ATC;
- more than one possible seed match

is sent to a review queue rather than silently included or excluded.

---

# 6. Family ATC scopes

FAM_STATINS:
C10AA

FAM_ARB:
C09CA

FAM_SSRI:
N06AB

FAM_DOAC:
B01AF, B01AE

FAM_DPP4:
A10BH

FAM_SGLT2:
A10BK

FAM_H1_ANTIHISTAMINE:
R06AE, R06AX

FAM_P2Y12:
B01AC

FAM_TRIPTAN:
N02CC

FAM_5HT3:
A04AA

FAM_ANTIPSYCHOTIC:
N05A

FAM_GLP1:
A10BJ

FAM_BISPHOSPHONATE:
M05BA

FAM_BENZO_SEIZURE:
N05BA, N05CD

Family membership still requires an explicit seed-ingredient match.

A matching ATC prefix alone is never sufficient.

---

# 7. Candidate-family eligibility counts

For product-universe eligibility, counts are based on:

1. distinct canonical seed active ingredients represented by at least one
   non-suspended eligible licence; and
2. distinct non-suspended licence numbers.

Preferred eligibility remains:

- at least 3 represented active ingredients;
- at least 6 eligible licensed medicinal products.

Protocol fallback remains:

- 2 represented active ingredients;
- at least 4 eligible licensed medicinal products.

Clinical eligibility remains a separate requirement.

---

# 8. Presentation metadata

For every retained licence, the following presentation-level information is
preserved when available:

- barcode;
- full product name;
- raw active-ingredient wording;
- ATC code;
- marketing-authorisation holder;
- suspension status.

Multiple presentation records are collapsed only for the primary
licence-level product count.

Raw presentation records remain auditable.

---

# 9. Review queue

The parser must explicitly report:

- unmatched seeded ATC records;
- multiple-seed matches;
- combination exclusions;
- missing licence numbers;
- missing ATC codes;
- unexpected ATC codes;
- mixed suspension states;
- conflicting marketing-authorisation-holder values.

No ambiguous record is silently resolved.

---

# 10. Separation from packaging analysis

During this phase the following information is prohibited from inclusion or
selection decisions:

- container;
- vial;
- ampoule;
- blister;
- bottle;
- stopper;
- closure;
- seal;
- carton;
- packaging supplier;
- manufacturing-site convergence.

Those variables are collected only after the therapeutic-family and product
universe has been frozen.

---

# 11. Benzodiazepine-family metadata correction

The original candidate registry contained the shorthand:

ATC_N05BA/N03AE_2026

This was corrected before product matching.

The seeded acute-seizure medicines map to:

- diazepam: N05BA01;
- lorazepam: N05BA06;
- midazolam: N05CD08.

This correction changes source metadata only and was made before family
selection or packaging extraction.