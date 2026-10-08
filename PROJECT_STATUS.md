# Project Status

> **STATUS: CLOSED — PUBLIC-DATA FEASIBILITY GATE FAILED**

## Original research question

Do multiple licensed therapeutic alternatives represent genuinely independent pharmaceutical supply redundancy, or can apparently distinct products share hidden physical dependencies and therefore create false redundancy?

The intended chain was:

`therapeutic alternatives -> hidden shared dependencies -> effective redundancy -> shock vulnerability / supply resilience`

## What was completed

The repository preserves a reproducible methodological/software checkpoint covering:

- deterministic product-universe and clinical-family construction;
- pharmaceutical-form reconciliation;
- parenteral PPI proof-of-concept work;
- component / packaging representations at multiple resolutions;
- partial-observability and site-resolution logic;
- evidence-sensitive versus resolution-sensitive overlap classifications;
- Stage-2 packaging schema and inference protocol;
- deterministic POC outputs;
- automated testing and clean-clone reproducibility.

Clean-clone freeze audit:

**157 passed**

## Why the research line is now closed

The final `5 target molecules + 1 positive control` GTİP/upstream-data feasibility gate was completed on 2026-10-08.

Targets:
- famotidine;
- omeprazole;
- pantoprazole;
- esomeprazole;
- dapagliflozin.

Positive control:
- o-acetylsalicylic acid.

Result:

- **5 / 5 project targets failed molecule-level public GTİP resolution.**
- The positive control passed.

The relevant target APIs map to broad residual chemical classes that contain multiple unrelated substances and/or have unstable mappings across salt/form/declaration contexts. Public aggregate GTİP trade statistics therefore cannot isolate the target molecule well enough to support upstream supplier-concentration or false-redundancy inference.

See:

`docs/PHARMA_GTIP_FEASIBILITY_GATE_FINAL_2026-10-08.md`

## Scientific boundary

This closure does **not** mean pharmaceutical supply resilience is unimportant or that false redundancy does not exist.

It means the original question is not identifiable at the required resolution using the tested **public-data-only** design.

Packaging diversity, documented facility names and broad GTİP classes must not be treated as proof of independent upstream supply paths.

## Final decision

No further work is required on the current pharma line.

Do not restart:
- large-scale KÜB collection;
- new clinical-family expansion;
- packaging canonicalisation;
- GTİP scraping;
- supply-network modelling based on these public aggregates.

A future reopening would require a materially different data source capable of identifying molecule-specific upstream supplier/API/manufacturing relationships. That would constitute a new research project.

## Final technical state

- repository checkpoint: frozen;
- clean clone: validated;
- test suite: **157 passed**;
- public-data GTİP feasibility gate: **FAILED**;
- research status: **CLOSED**.
