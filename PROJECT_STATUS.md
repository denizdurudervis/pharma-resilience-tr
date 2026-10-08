# Project Status

> **STATUS: PARKED — DATA-FEASIBILITY GATE PENDING**

## Original research question

Do multiple licensed therapeutic alternatives represent genuinely independent
pharmaceutical supply redundancy, or can apparently distinct products share
hidden physical dependencies and therefore create false redundancy?

The intended research logic was:

therapeutic alternatives -> hidden shared dependencies -> effective redundancy
-> shock vulnerability / supply resilience.

## What has been completed

The repository contains a reproducible methodological and software checkpoint
for:

- deterministic product-universe and clinical-family construction;
- pharmaceutical-form reconciliation;
- pilot analyses of parenteral PPI products;
- component / packaging representation at multiple canonical resolutions;
- partial-observability and site-resolution logic;
- evidence-sensitive versus resolution-sensitive overlap classifications;
- Stage-2 packaging schema and inference protocol;
- automated tests for the implemented checkpoint.

At the parked checkpoint, the full test suite passes:

**157 passed**

The deterministic POC summary is generated from:

- `data/manual/product_audit_v0_1.csv`
- `data/manual/component_audit_v0_1.csv`

using:

`python -m pharma_resilience.poc_results_summary data/manual/product_audit_v0_1.csv data/manual/component_audit_v0_1.csv --json-out data/processed/poc_results_summary_v0_1.json --md-out data/processed/poc_results_summary_v0_1.md`

## Why the project is parked

The original scientific question requires evidence about whether apparently
alternative products actually depend on independent upstream supply routes.

The tested public regulatory sources can document product attributes,
pharmaceutical form, packaging/component descriptions and some facility
information, but they do not establish supplier/site independence at the
resolution required for the original false-redundancy inference.

In particular:

- different KÜB wording does not necessarily imply different physical supply
  components;
- different packaging signatures do not prove independent suppliers;
- facility names in public documents do not necessarily establish exhaustive
  manufacturing roles or independent production routes;
- absence of a documented shared dependency is not evidence of operational
  redundancy.

Therefore the current packaging/KÜB layer is retained as exploratory
methodological work, not as proof of independent pharmaceutical supply routes.

## What is NOT claimed

This repository does not claim that:

- packaging diversity equals supplier diversity;
- different licensed products imply independent supply redundancy;
- a documented site is the unique or exhaustive manufacturing site;
- the current POC quantifies real national pharmaceutical shortage risk;
- the original false-redundancy research question has been scientifically
  resolved.

## Next research gate — only if this line is reopened

The sole next gate is:

**5 target molecules + 1 positive control -> GTİP / upstream-data resolution test**

No large-scale KÜB collection, new clinical-family expansion, or additional
packaging infrastructure should be started before that gate demonstrates that
upstream dependency information can actually be resolved at a scientifically
useful level.

If that gate fails, the appropriate decision is stop or pivot rather than
expanding the existing packaging dataset.
