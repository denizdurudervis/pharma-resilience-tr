# Audit Summary v0.1

Frozen 9-product audit sample; summary generated directly from the committed manual audit tables.

## Sample

- Products: **9**
- Products with both KÜB and KT evidence: **8/9**
- Products with neither KÜB nor KT evidence: **1/9**
- Portal exact-search no-match observations: **1**

## Process classes

- `lyophilized`: 7
- `liquid`: 1
- `unknown`: 1

## Container classes

- `type_I_clear_glass_vial`: 5
- `ampoule`: 1
- `type_I_clear_glass_powder_ampoule+type_I_clear_glass_solvent_ampoule`: 1
- `type_I_clear_glass_vial+type_I_clear_glass_solvent_ampoule`: 1
- `unknown`: 1

## Process × container

- `lyophilized × type_I_clear_glass_vial`: 5
- `liquid × ampoule`: 1
- `lyophilized × type_I_clear_glass_powder_ampoule+type_I_clear_glass_solvent_ampoule`: 1
- `lyophilized × type_I_clear_glass_vial+type_I_clear_glass_solvent_ampoule`: 1
- `unknown × unknown`: 1

## Route observation

- Known route signatures: **8/9 (88.9%)**
- Complete route observation: **False**
- Maximum observed route multiplicity: **5**
- Robustness-gap evaluable on observed routes: **True**
- Robustness-gap evaluable on full sample: **False**

## Cross-ingredient route convergence

| Route | Products | Active ingredients | Ingredients |
|---|---:|---:|---|
| `liquid|ampoule` | 1 | 1 | famotidin |
| `lyophilized|ampoule+solvent_ampoule` | 1 | 1 | famotidin |
| `lyophilized|vial` | 5 | 3 | esomeprazol, omeprazol, pantoprazol |
| `lyophilized|vial+solvent_ampoule` | 1 | 1 | famotidin |

## Manufacturing-site observability

- Products with at least one named production site: **8/9 (88.9%)**
- Products with multiple named production sites: **1**

## Evidence-field coverage

| Field | Products observed | Coverage |
|---|---:|---:|
| `active_ingredient` | 8/9 | 88.9% |
| `pharmaceutical_form` | 8/9 | 88.9% |
| `therapeutic_indication` | 8/9 | 88.9% |
| `atc_code` | 8/9 | 88.9% |
| `container_class` | 8/9 | 88.9% |
| `closure_class` | 4/9 | 44.4% |
| `marketing_authorisation_holder` | 8/9 | 88.9% |
| `license_id` | 8/9 | 88.9% |
| `manufacturing_site` | 8/9 | 88.9% |
| `site_role` | 0/9 | 0.0% |
| `site_list_exhaustiveness` | 0/9 | 0.0% |

## Route groups by active ingredient

### esomeprazol

- Products: 2
- Known route signatures: 2/2
- Complete route observation: True
- Maximum route multiplicity: 2
- Gap evaluable on observed routes: True

### famotidin

- Products: 3
- Known route signatures: 3/3
- Complete route observation: True
- Maximum route multiplicity: 1
- Gap evaluable on observed routes: False

### omeprazol

- Products: 2
- Known route signatures: 1/2
- Complete route observation: False
- Maximum route multiplicity: 1
- Gap evaluable on observed routes: False

### pantoprazol

- Products: 2
- Known route signatures: 2/2
- Complete route observation: True
- Maximum route multiplicity: 2
- Gap evaluable on observed routes: True

