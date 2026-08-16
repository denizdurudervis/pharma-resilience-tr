# Protocol v0.1 — Frozen before the site audit

## Objective

Determine whether public Turkish pharmaceutical documents contain enough
role-resolved production information to support a physical supply-resilience model.

## Audit sample

5–10 licensed products. The initial audit is a **data-access gate**, not an
effect-estimation sample.

## Required evidence fields

For every product/document pair record:

1. document type and date/version
2. site name
3. site role/stage
4. required / alternative / unknown relation
5. whether the listed sites are explicitly exhaustive
6. process class
7. container/closure information
8. field resolution: explicit / partial / ambiguous / absent
9. cross-source conflicts

## Frozen assumptions

### Hidden alternatives
`m_plus` controls sensitivity to unobserved alternative/backup sites.
These improve optimistic bounds but do not worsen the baseline robust solution.

### Hidden common mandatory dependencies
Baseline uses `m_minus = 0`.
Unobserved common mandatory production dependencies are not adversarially
invented without documentary support. This is a scope assumption, not a claim
that such dependencies do not exist.

### Decision rule

If a clinical coverage threshold `eta` is defined:

- global lower bound >= eta -> robust pass
- global upper bound < eta -> robust fail
- otherwise -> indeterminate

If only a subset of uncertainty axes is released, label the result conditional.

If no decision threshold is defined, use the pre-specified descriptive width
gate:

- width <= 0.25 -> descriptively identifiable
- width > 0.25 -> no point conclusion

## Go / no-go for the site arm

Proceed to a full site-interdiction model only if the audit shows that site role,
relation and exhaustiveness can be bounded tightly enough to yield informative
decision-relevant coverage bounds.

Otherwise:

- retain MAH and documented route results;
- downgrade site analysis to descriptive named-site evidence;
- do not report a point-estimate physical redundancy or site min-cut.

## Data-quality pipeline

- do not rely on ATC alone;
- independently scan active ingredient fields;
- normalize Turkish text;
- run root/fuzzy review for near-matches;
- print every fuzzy/near match for manual adjudication;
- never silently accept a fuzzy match;
- record source conflicts explicitly.

## Macro layer

The TÜİK A64 layer is coarse but structurally observed.
It may be used for deterministic common-mode scenario propagation.
Do not place CVaR or expected-risk language on macro shocks without an
externally justified shock probability law.

## Next milestone

Complete the 5–10 product audit before expanding the optimization model.
