# Pharmaceutical Component Resolution Sensitivity v0.1

Observed product-component convergence evaluated at increasingly coarse physical component resolution.

**Important:** aggregation changes descriptive component identity only. It does not establish supplier identity, mandatory dependence, non-substitutability, or a common failure mode.

## Resolution definitions

- `R0_exact`: exact normalized component class.
- `R1_parent`: one observed parent step.
- `R2_terminal`: transitive observed parent family.

## Resolution summary

| Level | Component classes | Product-component edges | Cross-ingredient classes |
|---|---:|---:|---:|
| `R0_exact` | 9 | 17 | 3 |
| `R1_parent` | 6 | 17 | 4 |
| `R2_terminal` | 5 | 17 | 3 |

## R0_exact

| Component class | Products | Active ingredients | Exact classes collapsed |
|---|---:|---:|---:|
| `type_I_clear_glass_vial` | 6 | 4 | 1 |
| `bromobutyl_lyophilization_stopper` | 2 | 2 | 1 |
| `bromobutyl_rubber_stopper` | 2 | 2 | 1 |
| `type_I_clear_glass_ampoule` | 2 | 1 | 1 |
| `aluminium_cap` | 1 | 1 | 1 |
| `aluminium_crimp_cap_with_polypropylene_cap` | 1 | 1 | 1 |
| `aluminium_flip_off_cap` | 1 | 1 | 1 |
| `flip_off_cap` | 1 | 1 | 1 |
| `type_I_amber_neutral_borosilicate_glass_ampoule` | 1 | 1 | 1 |

## R1_parent

| Component class | Products | Active ingredients | Exact classes collapsed |
|---|---:|---:|---:|
| `glass_vial` | 6 | 4 | 1 |
| `aluminium_cap` | 3 | 3 | 3 |
| `bromobutyl_rubber_stopper` | 2 | 2 | 1 |
| `rubber_stopper` | 2 | 2 | 1 |
| `glass_ampoule` | 3 | 1 | 2 |
| `cap` | 1 | 1 | 1 |

## R2_terminal

| Component class | Products | Active ingredients | Exact classes collapsed |
|---|---:|---:|---:|
| `glass_vial` | 6 | 4 | 1 |
| `rubber_stopper` | 4 | 3 | 2 |
| `aluminium_cap` | 3 | 3 | 3 |
| `glass_ampoule` | 3 | 1 | 2 |
| `cap` | 1 | 1 | 1 |

## Interpretation

If observed convergence increases as resolution becomes coarser, the apparent redundancy structure is resolution-dependent.

Conversely, convergence that persists at exact resolution is supported without requiring parent-family aggregation.

