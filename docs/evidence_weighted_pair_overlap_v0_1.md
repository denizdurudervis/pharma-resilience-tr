# Evidence-Weighted Ingredient-Pair Component Overlap v0.1

Observed component convergence weighted by frozen-sample documentary support.

**Critical interpretation rule:** the `componentwise_unresolved_envelope_score` is a sensitivity envelope, not a jointly feasible physical upper bound and not a probability.

## Summary

| Level | Pairs | Mean documented overlap | Mean unresolved envelope | Maximum documented |
|---|---:|---:|---:|---:|
| `R0_exact` | 6 | 0.667 | 1.389 | 1.500 |
| `R1_parent` | 6 | 0.917 | 1.417 | 2.000 |
| `R2_terminal` | 6 | 1.000 | 1.417 | 2.000 |

## R0_exact

| Ingredient pair | Existential classes | Documented overlap | Unresolved envelope | Envelope increment |
|---|---:|---:|---:|---:|
| esomeprazol – pantoprazol | 2 | 1.500 | 1.500 | 0.000 |
| omeprazol – pantoprazol | 2 | 1.000 | 3.000 | 2.000 |
| esomeprazol – omeprazol | 1 | 0.500 | 2.000 | 1.500 |
| famotidin – omeprazol | 1 | 0.333 | 1.167 | 0.833 |
| esomeprazol – famotidin | 1 | 0.333 | 0.333 | 0.000 |
| famotidin – pantoprazol | 1 | 0.333 | 0.333 | 0.000 |

## R1_parent

| Ingredient pair | Existential classes | Documented overlap | Unresolved envelope | Envelope increment |
|---|---:|---:|---:|---:|
| esomeprazol – pantoprazol | 3 | 2.000 | 2.000 | 0.000 |
| omeprazol – pantoprazol | 3 | 1.500 | 3.000 | 1.500 |
| esomeprazol – omeprazol | 2 | 1.000 | 2.000 | 1.000 |
| famotidin – omeprazol | 1 | 0.333 | 0.833 | 0.500 |
| esomeprazol – famotidin | 1 | 0.333 | 0.333 | 0.000 |
| famotidin – pantoprazol | 1 | 0.333 | 0.333 | 0.000 |

## R2_terminal

| Ingredient pair | Existential classes | Documented overlap | Unresolved envelope | Envelope increment |
|---|---:|---:|---:|---:|
| esomeprazol – pantoprazol | 3 | 2.000 | 2.000 | 0.000 |
| omeprazol – pantoprazol | 3 | 1.500 | 3.000 | 1.500 |
| esomeprazol – omeprazol | 3 | 1.500 | 2.000 | 0.500 |
| famotidin – omeprazol | 1 | 0.333 | 0.833 | 0.500 |
| esomeprazol – famotidin | 1 | 0.333 | 0.333 | 0.000 |
| famotidin – pantoprazol | 1 | 0.333 | 0.333 | 0.000 |

## Interpretation

The existential count answers whether a component class appears anywhere in both active-ingredient product portfolios.

The documented overlap score additionally reflects how many frozen-sample products have explicit documentary support for those component classes.

The unresolved envelope shows sensitivity to products without any explicit component evidence. It must not be interpreted as a physically achievable simultaneous configuration.

