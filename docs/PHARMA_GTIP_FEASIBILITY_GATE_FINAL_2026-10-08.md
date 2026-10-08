# PHARMA-RESILIENCE-TR
## Final GTİP / Upstream-Data Feasibility Gate
**Freeze date:** 2026-10-08  
**Decision purpose:** Decide whether the original false-redundancy research line can be continued using public, reproducible Turkish trade-classification data without starting a new proprietary-data project.

---

## 1. Original scientific requirement

The original project asks whether apparently alternative licensed medicines are truly independent supply alternatives or whether they hide shared upstream dependencies.

For GTİP-based trade data to rescue that question, public trade statistics must resolve an active pharmaceutical ingredient (API) narrowly enough that country-level import value/quantity can be interpreted as evidence about that API rather than about a large mixed chemical class.

A GTİP code is **not sufficient** merely because shipments containing the target API have been declared under it. The code must be sufficiently specific that the public aggregate can be attributed to the target molecule with defensible selectivity.

---

## 2. Gate design

No exact five-molecule-plus-control set was preserved in the earlier checkpoint. To avoid reopening the whole selection problem, this final gate freezes a lineage-based set:

### Five targets
1. **Famotidine** — original parenteral PPI/H2-blocker proof-of-concept ingredient.
2. **Omeprazole** — original proof-of-concept ingredient.
3. **Pantoprazole** — original proof-of-concept ingredient.
4. **Esomeprazole** — original proof-of-concept ingredient.
5. **Dapagliflozin** — representative of the previously selected Stage-2 SGLT2 family.

### Positive control
6. **O-acetylsalicylic acid (acetylsalicylic acid / aspirin API)** — selected because HS nomenclature contains a dedicated molecule-level subheading (HS 291822), allowing the gate to distinguish “the method cannot work at all” from “the selected pharma targets are not publicly resolvable”.

The five targets were chosen from the project's existing line of work, not because of a favourable tariff result.

---

## 3. Decision rule

### PASS for a target
A target passes only if public classification/trade data provide a stable molecule-specific code (or an equivalently selective public mapping) such that partner-country import statistics can reasonably be interpreted as imports of that target API.

### FAIL for a target
A target fails if any of the following holds:
- the target is mapped to a residual “other” chemical class containing many unrelated compounds;
- multiple salts/forms/declaration contexts produce unstable mappings;
- public aggregate statistics cannot isolate the target from unrelated products sharing the code;
- molecule identity is recoverable only from shipment-description text in proprietary/non-exhaustive commercial databases rather than from the public classification itself.

### Gate-level rule
The public-data route is considered infeasible for the original study if at least 3 of the 5 targets fail molecule-level resolution.

The positive control must pass; otherwise the test itself would be uninformative.

---

## 4. Public-data infrastructure check

TÜİK states that Turkish foreign-trade statistics are compiled using **12-digit GTİP** codes. The 2026 GTİP classification is available in the TÜİK classification server. TÜİK's foreign-trade microdata documentation includes GTİP, partner/origin country, quantity and monetary-value fields.

Therefore the bottleneck is **not the absence of Turkish trade data**. The bottleneck is whether the target APIs have sufficiently selective public tariff positions.

---

## 5. Molecule-level resolution audit

| Molecule | Observed / relevant GTİP family | Public code semantics | Resolution verdict | Reason |
|---|---|---|---|---|
| Famotidine | `293410000019` appears for API/raw-material declarations | Broad residual thiazole class (“other” compounds containing an unfused thiazole ring) | **FAIL** | The same code is used for unrelated compounds such as meloxicam and pioglitazone in shipment records. Aggregate GTİP totals therefore cannot be interpreted as famotidine totals. |
| Omeprazole | `293339990039` appears repeatedly for API/raw-material declarations; other contexts also occur | Broad residual pyridine-containing heterocyclic class | **FAIL** | The code is not molecule-specific and is used for many unrelated APIs/chemicals. Mapping also varies across declaration contexts. |
| Pantoprazole | `293339990039` appears repeatedly for pantoprazole sodium/API | Same broad residual pyridine-containing heterocyclic class | **FAIL** | Pantoprazole shares the code with omeprazole, esomeprazole and unrelated compounds; public aggregate data cannot isolate pantoprazole. |
| Esomeprazole | `293339990039` appears repeatedly; alternative codes also occur in some declaration contexts | Same broad residual pyridine-containing heterocyclic class | **FAIL** | Same-code sharing and mapping variation prevent defensible molecule-level aggregation. |
| Dapagliflozin | `293299009029` appears for API/raw-material declarations | Broad residual oxygen-heterocyclic class (“other”) | **FAIL** | The same code is used for unrelated substances including other pharmaceutical raw materials; public aggregate GTİP totals cannot isolate dapagliflozin. |
| O-acetylsalicylic acid | HS `291822` | Dedicated subheading for o-acetylsalicylic acid, its salts and esters | **PASS (positive control)** | Public Turkey import data by partner country are available at this molecule-specific HS6 subheading, demonstrating that the trade-data approach works when nomenclature is sufficiently specific. |

---

## 6. Critical cross-check: same GTİP, different chemicals

The decisive problem is not theoretical. Public/secondary shipment evidence shows that the same Turkish residual codes used by the targets are also used for unrelated chemicals:

- `293339990039` is a generic pyridine-containing heterocyclic residual class and appears with pantoprazole, omeprazole, esomeprazole and unrelated compounds.
- `293410000019` is a generic thiazole residual class and appears with famotidine as well as unrelated pharmaceutical/chemical substances.
- `293299009029` is a generic oxygen-heterocyclic residual class and appears with dapagliflozin and unrelated pharmaceutical raw materials.

A country-level import total for any of these codes is therefore a **mixture**, not a molecule-level upstream-flow measure.

Commercial shipment databases may expose free-text product descriptions that contain molecule names. That does not rescue the public-only design because:
1. those description-level datasets are proprietary/non-exhaustive;
2. the target may appear under multiple codes/forms;
3. declaration text is not a stable public classification key;
4. using a commercial shipment dataset would constitute a new data-acquisition project with different reproducibility and coverage assumptions.

---

## 7. Gate result

### Target results
- Famotidine: **FAIL**
- Omeprazole: **FAIL**
- Pantoprazole: **FAIL**
- Esomeprazole: **FAIL**
- Dapagliflozin: **FAIL**

**Target pass rate: 0 / 5**

### Positive control
- O-acetylsalicylic acid: **PASS**

The control demonstrates that the gate is capable of detecting a usable molecule-specific trade classification when one exists.

## FINAL GATE VERDICT: **FAIL — PUBLIC GTİP DATA ARE NOT SUFFICIENT FOR THE ORIGINAL FALSE-REDUNDANCY QUESTION**

---

## 8. Research decision

The pharma false-redundancy line should now move from:

`PARKED — DATA-FEASIBILITY GATE PENDING`

to:

# `CLOSED — PUBLIC-DATA FEASIBILITY GATE FAILED`

This is not a negative result about the scientific importance of pharmaceutical supply resilience. It is a decision about **identifiability under the chosen public-data design**.

The implemented packaging/site/partial-observability framework remains a valid technical checkpoint, but it should not be expanded into a national false-redundancy claim using public GTİP aggregates.

No further KÜB collection, family expansion, packaging canonicalisation, GTİP scraping or network modelling is required for this line.

---

## 9. What would be required to reopen the project

Reopening would require a materially different data source, for example:
- molecule-specific transaction-level customs data with validated coverage;
- manufacturer/API-supplier linkage data;
- regulatory supply-chain data identifying API source and manufacturing roles;
- licensed commercial data with an explicit completeness/validation study.

Obtaining or validating such data would be a **new research project**, not completion of the current one.

---

## 10. Final scope statement

As of 2026-10-08:

- technical repository checkpoint: reproducible;
- clean-clone test suite: **157 passed**;
- original public-data false-redundancy question: **not identifiable at required resolution**;
- GTİP feasibility gate: **failed on 5/5 project targets**;
- positive control: **passed**;
- project status: **CLOSED**.

There is no remaining mandatory technical work on this research line.

---

## Sources used for the gate

Primary/public classification infrastructure:
1. TÜİK, *Dış Ticaret İstatistikleri — Metadata* (2026): Turkish foreign-trade statistics use 12-digit GTİP.
2. TÜİK, *Sınıflama Sunucusu — GTİP 2026*: 2026 national tariff classification is published.
3. TÜİK, *Dış Ticaret Mikro Veri Seti*: GTİP, partner/origin country, quantity and monetary-value fields are documented.
4. T.C. Sanayi ve Teknoloji Bakanlığı, *Öncelikli Ürün Listesi Tebliği*: includes generic residual descriptions such as `293339990039` and `293299009029`.
5. UNSD HS classification: HS `291822` is o-acetylsalicylic acid, its salts and esters.
6. World Bank WITS / UN Comtrade: Turkey partner-country import data are publicly available for HS `291822`.

Secondary diagnostic evidence:
7. Commercial shipment-index pages (Volza and similar) were used only to verify that the broad residual Turkish codes are in practice shared by the target molecules and unrelated chemicals. These sources were **not** used to estimate market shares, supplier concentration or national totals.

### Source URLs
- https://veriportali.tuik.gov.tr/tr/press/58239/metadata
- https://siniflama.tuik.gov.tr/Classifications/ClassificationsTurDetay?tur=3
- https://www.tuik.gov.tr/media/microdata/pdf/dis-ticaret.pdf
- https://www.sanayi.gov.tr/assets/pdf/mevzuat/OncelikliUrunListesiTebligi.pdf
- https://unstats.un.org/unsd/classifications/Econ/Detail/EN/32/291822
- https://wits.worldbank.org/trade/comtrade/en/country/TUR/year/2023/tradeflow/Imports/partner/ALL/product/291822
