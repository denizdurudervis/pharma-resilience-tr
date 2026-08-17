# Packaging Resolution-Sensitivity Checkpoint — 2026-08-18

## Status

The packaging/component branch is no longer treated as a definitive
scaling gate for the pharmaceutical resilience analysis.

Gate-A is retained as a screening / identifiability diagnostic.

## PPI evidence state

Initial parenteral PPI evidence universe:

- 46 licences
- 39 main-evidence CONFIRMED
- 7 explicit UNKNOWN
- frozen initial hold registry: 8 licences
- first hold-resolution assessment: 8 / 8 completed

The seven UNKNOWN records are evidence gaps, not unreviewed records.

## Gate-A methodological audit

The original global Gate-A statistics were found to be dominated by a
single informative pharmaceutical-form stratum.

Complete-case audit:

- n = 6
- pharmaceutical-form strata = 4
- H(S) = 2.584963
- H(S|F) = 0.792481
- residual entropy ratio = 0.306574
- modal signature prediction error = 0.333333
- signature_determined_by_form = False

The global statistics do not constitute independent pieces of evidence:
the informative variation comes from the repeated lyophilized-powder
stratum, while the remaining complete-case strata are singletons.

## Robust within-form stratum

The cleanest repeated stratum contained three independently identified
products:

- OMEPROL — licence 126/89 — Sandoz
- GASTRAZOL-L — licence 218/91
- JECTOPAN — licence 2024/239 — Tüm Ekip

All three are:

- pharmaceutical_form = lyophilized_powder
- container_class = type_I_clear_glass_vial

The three licences were independently confirmed against the frozen TITCK
source workbook.

## Resolution-sensitivity result

Observed closure/component signatures were re-expressed at three
resolutions.

Result:

- verbatim document wording: 3 distinct signatures
- supported canonical resolution: 2 distinct signatures
- coarse system-family sensitivity: 1 distinct signature

Therefore the apparent packaging heterogeneity is resolution-sensitive.

The coarse collapse to one signature is a sensitivity experiment and
must NOT be interpreted as proof that the physical closure systems are
identical.

The supported interpretation is narrower:

Public product documents describe container-closure components at
heterogeneous levels of granularity, so physical packaging redundancy
cannot be identified reliably from verbatim wording alone.

## Decision

Do NOT expand the packaging/component extraction to all therapeutic
families at this stage.

Do NOT use the original residual-entropy threshold as a scientific
scaling rule.

Retain packaging as an identifiability / resolution-sensitivity finding.

The site layer is treated analogously as an identifiability diagnostic
because site_name may be observed while role, relation, and
exhaustiveness remain unresolved.

## Main modelling path

The primary resilience analysis now proceeds through:

1. deterministic therapeutic product universe;
2. active-licence / clinical eligibility;
3. pharmaceutical form / route redundancy;
4. MAH concentration and corporate dependence;
5. correlated upstream / input-output shocks.

Packaging and site evidence remain diagnostic side layers rather than
unverified network edges.

## Next session

Start from route/form redundancy.

Do not resume large-scale KUB 6.5 packaging extraction unless a new,
explicitly justified identification strategy is introduced.
