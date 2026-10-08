> **RESEARCH STATUS: PARKED — DATA-FEASIBILITY GATE PENDING**
>
> The implemented technical checkpoint is frozen and reproducible. The original
> false-redundancy question is **not** considered scientifically resolved because
> the tested public-data route does not establish independent upstream supply
> paths. See [`PROJECT_STATUS.md`](PROJECT_STATUS.md).
# Pharmaceutical Resilience under Partial Observability â€” TÃ¼rkiye

Research codebase for a staged study of pharmaceutical supply resilience in TÃ¼rkiye.

## Core question

How should inventory and diversification decisions be made when:
1. macroeconomic production links are observed only at coarse inputâ€“output resolution;
2. product-level routes are observable from public regulatory documents;
3. physical manufacturing topology (site roles, AND/OR relations, exhaustiveness) is only partially observed?

## v0.1 scope

This version does **not** claim to estimate the true physical supply network.
It first runs a 5â€“10 product data-access audit.

The audit decides whether the site/topology arm is identifiable enough to justify a larger optimization model.

## Frozen principles

- Marketing-authorisation-holder (MAH) concentration is not manufacturing-site concentration.
- Product-route information and manufacturing-site information are separate layers.
- Unknown relations are not silently converted into AND or OR edges.
- `m_plus` = maximum unobserved alternative-site allowance in sensitivity analysis.
- Baseline assumes `m_minus = 0`: unobserved common mandatory dependencies are not adversarially invented unless documentary evidence supports them.
- Macro shocks are scenario analyses unless a probability law is externally justified.
- CVaR-style interpretation is used only for the capped-simplex product-weight uncertainty axis.
- Raw registry files are not committed unless redistribution is clearly permitted; hashes and provenance should be recorded.

## Immediate milestone

Populate:

- `templates/product_audit.csv`
- `templates/evidence_audit.csv`

for 5â€“10 products.

Then compute field observability and topology-width diagnostics before scaling up.

## Repository layout

- `src/pharma_resilience/filters.py` â€” text normalization and fuzzy-review flags
- `src/pharma_resilience/mah.py` â€” MAH descriptive resilience statistics
- `src/pharma_resilience/route_robustness.py` â€” exact random/targeted route-retention curves
- `src/pharma_resilience/audit.py` â€” document-field completeness metrics
- `src/pharma_resilience/topology.py` â€” topology-bound scaffolding
- `src/pharma_resilience/io_bridge.py` â€” explicit interface to the frozen A64 engine
- `templates/` â€” manual audit tables
- `docs/protocol_v0.1.md` â€” frozen pre-analysis protocol

## Status

Design frozen; empirical audit is the next gate.

