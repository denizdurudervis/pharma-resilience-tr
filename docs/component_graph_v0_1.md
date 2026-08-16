# Component-Level Pharmaceutical Dependency Graph v0.1

Generated automatically from the frozen component audit table.

**Interpretation rule:** observed component convergence is descriptive and does not by itself establish supplier identity, mandatory dependence, non-substitutability, or a common failure mode.

## Graph summary

- Audit rows: **19**
- Products: **9**
- Explicit component observations: **18**
- Exact physical component classes: **9**
- Unique product-component relationships: **17**
- Shared component classes: **4**
- Cross-ingredient component classes: **3**

## Coverage

- Products with at least one explicit component: **8/9**
- Unresolved products: **1**
  - `OMHEAL_2025_605`

## Cross-ingredient exact component convergence

| Component class | Products | Active ingredients | Ingredients | Roles |
|---|---:|---:|---|---|
| `type_I_clear_glass_vial` | 6 | 4 | esomeprazol, famotidin, omeprazol, pantoprazol | primary_container |
| `bromobutyl_lyophilization_stopper` | 2 | 2 | esomeprazol, pantoprazol | closure |
| `bromobutyl_rubber_stopper` | 2 | 2 | omeprazol, pantoprazol | closure |

## All exact component classes

| Component class | Products | Active ingredients | Roles | Parent |
|---|---:|---:|---|---|
| `type_I_clear_glass_vial` | 6 | 4 | primary_container | glass_vial |
| `bromobutyl_lyophilization_stopper` | 2 | 2 | closure | bromobutyl_rubber_stopper |
| `bromobutyl_rubber_stopper` | 2 | 2 | closure | rubber_stopper |
| `type_I_clear_glass_ampoule` | 2 | 1 | primary_container, solvent_container | glass_ampoule |
| `aluminium_cap` | 1 | 1 | seal | aluminium_cap |
| `aluminium_crimp_cap_with_polypropylene_cap` | 1 | 1 | seal | aluminium_cap |
| `aluminium_flip_off_cap` | 1 | 1 | seal | aluminium_cap |
| `flip_off_cap` | 1 | 1 | seal | cap |
| `type_I_amber_neutral_borosilicate_glass_ampoule` | 1 | 1 | primary_container | glass_ampoule |

## Methodological note

Component identity is defined by the normalized physical `component_class`. Product-specific roles such as `primary_container` and `solvent_container` are retained on the relationship rather than used to create separate physical component identities.

This prevents the same physical component class from being artificially split merely because it serves different roles in different authorised product presentations.

Parent-component information is retained but is not collapsed in this exact-resolution analysis. Parent-level convergence will be evaluated separately in the multiresolution sensitivity analysis.

