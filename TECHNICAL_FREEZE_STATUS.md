# Technical Freeze Status

**Freeze date:** 2026-10-08  
**Repository:** `denizdurudervis/pharma-resilience-tr`  
**Research status:** PARKED — DATA-FEASIBILITY GATE PENDING

## Reproduction check

A fresh clone of the repository was used for the freeze audit.

Initial clean-clone test collection exposed two packaging dependencies that were
not declared in `pyproject.toml`:

- `matplotlib`
- `openpyxl`

These dependencies are now declared in the project metadata.

The POC result summary required by four tests was regenerated deterministically
from the versioned manual audit inputs:

- `data/manual/product_audit_v0_1.csv`
- `data/manual/component_audit_v0_1.csv`

Generated freeze artefacts:

- `data/processed/poc_results_summary_v0_1.json`
- `data/processed/poc_results_summary_v0_1.md`

## Test result

`python -m pytest -q`

**157 passed**

## Scientific boundary

This freeze preserves the implemented methodology and exploratory evidence.
It does not convert the parked project into a completed false-redundancy study.

The unresolved scientific requirement is independent upstream
supplier/site/API-route observability.

## Reopen condition

Only reopen the research line for the predefined:

**5 target molecules + 1 positive control -> GTİP / upstream-data feasibility gate.**
