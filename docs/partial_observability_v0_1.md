# Partial Observability Bounds v0.1

Compatibility bounds for convergence under missing dependency attributes.

Unknown fields are treated as wildcards only for upper-bound calculations. No missing value is imputed as equal or different.

| Level | Complete | Largest group LB | Largest group UB | Ingredient span LB | Ingredient span UB | Certain cross-ingredient? | Possible cross-ingredient? |
|---|---:|---:|---:|---:|---:|---|---|
| `R0_process` | 8/9 (88.9%) | 7 | 8 | 4 | 4 | True | True |
| `R1_process_container` | 8/9 (88.9%) | 5 | 6 | 3 | 3 | True | True |
| `R2_process_container_closure` | 6/9 (66.7%) | 1 | 3 | 1 | 3 | False | True |
| `R3_process_container_closure_named_site` | 5/9 (55.6%) | 1 | 2 | 1 | 2 | False | True |

## Upper-bound witnesses

### R0_process

- Largest compatible group: **8**
- Compatible signature: `lyophilized`
- Products: GASTRAZOLL_218_91, JECTOPAN_2024_239, NEVOFAML_2022_12, OMEPROL_126_89, OMHEAL_2025_605, PROKSIFAM_2018_22, REFASTIL_2014_3, REFLOSEL_2024_563
- Maximum compatible active-ingredient span: **4**
- Ingredients: esomeprazol, famotidin, omeprazol, pantoprazol

### R1_process_container

- Largest compatible group: **6**
- Compatible signature: `lyophilized | type_I_clear_glass_vial`
- Products: GASTRAZOLL_218_91, JECTOPAN_2024_239, OMEPROL_126_89, OMHEAL_2025_605, REFASTIL_2014_3, REFLOSEL_2024_563
- Maximum compatible active-ingredient span: **3**
- Ingredients: esomeprazol, omeprazol, pantoprazol

### R2_process_container_closure

- Largest compatible group: **3**
- Compatible signature: `lyophilized | type_I_clear_glass_vial | bromobutyl_lyophilization_stopper+aluminum_flip_off_cap`
- Products: OMHEAL_2025_605, REFASTIL_2014_3, REFLOSEL_2024_563
- Maximum compatible active-ingredient span: **3**
- Ingredients: esomeprazol, omeprazol, pantoprazol

### R3_process_container_closure_named_site

- Largest compatible group: **2**
- Compatible signature: `liquid | ampoule | not_applicable | Gensenta İlaç Sanayi ve Ticaret A.Ş. - Yenibosna/Bahçelievler/İstanbul`
- Products: FABOS_2017_14, OMHEAL_2025_605
- Maximum compatible active-ingredient span: **2**
- Ingredients: famotidin, omeprazol

