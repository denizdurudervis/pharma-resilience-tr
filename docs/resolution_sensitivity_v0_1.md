# Resolution Sensitivity v0.1

Multiresolution convergence analysis for the frozen pharmaceutical audit sample.

R3 uses the named production site reported in public documents. It does not establish site role or site-list exhaustiveness.

## Available-case analysis

| Level | Observed | Coverage | Signatures | Largest group | Cross-ingredient signatures | Max ingredient span |
|---|---:|---:|---:|---:|---:|---:|
| `R0_process` | 8/9 | 88.9% | 2 | 7 | 1 | 4 |
| `R1_process_container` | 8/9 | 88.9% | 4 | 5 | 1 | 3 |
| `R2_process_container_closure` | 6/9 | 66.7% | 6 | 1 | 0 | 1 |
| `R3_process_container_closure_named_site` | 5/9 | 55.6% | 5 | 1 | 0 | 1 |

## Complete-case resolution sensitivity

The complete-case panel fixes the product set to products observable at R3, preventing changes in missingness from being mistaken for changes caused by resolution.

- Complete-case products: **5/9**

| Level | Observed | Coverage | Signatures | Largest group | Cross-ingredient signatures | Max ingredient span |
|---|---:|---:|---:|---:|---:|---:|
| `R0_process` | 5/5 | 100.0% | 1 | 5 | 1 | 4 |
| `R1_process_container` | 5/5 | 100.0% | 2 | 4 | 1 | 3 |
| `R2_process_container_closure` | 5/5 | 100.0% | 5 | 1 | 0 | 1 |
| `R3_process_container_closure_named_site` | 5/5 | 100.0% | 5 | 1 | 0 | 1 |

## Cross-ingredient convergence by resolution

### R0_process

- `lyophilized`: 7 products; 4 active ingredients (esomeprazol, famotidin, omeprazol, pantoprazol)

### R1_process_container

- `lyophilized|type_I_clear_glass_vial`: 5 products; 3 active ingredients (esomeprazol, omeprazol, pantoprazol)

### R2_process_container_closure

No observed signature spans multiple active ingredients.

### R3_process_container_closure_named_site

No observed signature spans multiple active ingredients.

