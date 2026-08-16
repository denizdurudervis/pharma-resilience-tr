# Active-Ingredient Pair Component Convergence v0.1

Pairwise structural overlap in observed pharmaceutical component classes across dependency-resolution levels.

**Interpretation:** a shared component class indicates observed component-level convergence. It does not by itself establish common suppliers, mandatory dependence, non-substitutability, or a common failure mode.

## Summary

| Level | Ingredient pairs | Pairs with overlap | Mean shared components | Maximum |
|---|---:|---:|---:|---:|
| `R0_exact` | 6 | 6 | 1.333 | 2 |
| `R1_parent` | 6 | 6 | 1.833 | 3 |
| `R2_terminal` | 6 | 6 | 2.000 | 3 |

## R0_exact

| Ingredient pair | Shared components | Jaccard | Delta from previous level | Components |
|---|---:|---:|---:|---|
| esomeprazol – pantoprazol | 2 | 0.333 | NA | `bromobutyl_lyophilization_stopper`, `type_I_clear_glass_vial` |
| omeprazol – pantoprazol | 2 | 0.333 | NA | `bromobutyl_rubber_stopper`, `type_I_clear_glass_vial` |
| esomeprazol – famotidin | 1 | 0.200 | NA | `type_I_clear_glass_vial` |
| esomeprazol – omeprazol | 1 | 0.200 | NA | `type_I_clear_glass_vial` |
| famotidin – omeprazol | 1 | 0.200 | NA | `type_I_clear_glass_vial` |
| famotidin – pantoprazol | 1 | 0.143 | NA | `type_I_clear_glass_vial` |

## R1_parent

| Ingredient pair | Shared components | Jaccard | Delta from previous level | Components |
|---|---:|---:|---:|---|
| esomeprazol – pantoprazol | 3 | 0.600 | 1 | `aluminium_cap`, `bromobutyl_rubber_stopper`, `glass_vial` |
| omeprazol – pantoprazol | 3 | 0.600 | 1 | `aluminium_cap`, `glass_vial`, `rubber_stopper` |
| esomeprazol – omeprazol | 2 | 0.500 | 1 | `aluminium_cap`, `glass_vial` |
| esomeprazol – famotidin | 1 | 0.250 | 0 | `glass_vial` |
| famotidin – omeprazol | 1 | 0.250 | 0 | `glass_vial` |
| famotidin – pantoprazol | 1 | 0.167 | 0 | `glass_vial` |

## R2_terminal

| Ingredient pair | Shared components | Jaccard | Delta from previous level | Components |
|---|---:|---:|---:|---|
| esomeprazol – omeprazol | 3 | 1.000 | 1 | `aluminium_cap`, `glass_vial`, `rubber_stopper` |
| esomeprazol – pantoprazol | 3 | 0.750 | 0 | `aluminium_cap`, `glass_vial`, `rubber_stopper` |
| omeprazol – pantoprazol | 3 | 0.750 | 0 | `aluminium_cap`, `glass_vial`, `rubber_stopper` |
| esomeprazol – famotidin | 1 | 0.250 | 0 | `glass_vial` |
| famotidin – omeprazol | 1 | 0.250 | 0 | `glass_vial` |
| famotidin – pantoprazol | 1 | 0.200 | 0 | `glass_vial` |

## Methodological note

The analysis uses presence/absence sets at the active-ingredient level. Multiple products containing the same active ingredient therefore expand the ingredient's observed component set but do not directly weight a component by the number of products.

Product-level redundancy and evidence-bounded disruption analysis are separate downstream tasks.

