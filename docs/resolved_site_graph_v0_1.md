# Resolved Site Graph v0.1

Application of manually audited site-entity resolution decisions to the frozen product sample.

> Resolved facility identity does not establish mandatory product dependence.

## Resolution summary

- Raw site mentions: **9**
- Site observations: **9**
- Resolved facility entities: **2**
- Raw mentions assigned to resolved facilities: **3**
- Unresolved raw site mentions: **6**
- Cross-ingredient resolved facilities: **1**

## Resolved facilities

| Facility | Raw mentions | Products | Active ingredients | Ingredients | Interdiction ready? |
|---|---:|---:|---:|---|---|
| `FACILITY_VEM_KAPAKLI_001` | 1 | 1 | 1 | famotidin | False |
| `FACILITY_YENIBOSNA_SANAYI13_001` | 2 | 2 | 2 | famotidin, pantoprazol | False |

## Unresolved site mentions

- `HAVER TRAKYA İlaç San. ve Tic. A.Ş., Ergene/Tekirdağ` — 1 product(s)
- `Lek Pharmaceuticals d.d., Slovenia` — 1 product(s)
- `Mefar İlaç San. A.Ş.` — 1 product(s)
- `Mefar İlaç San. A.Ş., Ramazanoğlu Mah. Ensar Cad. No:20, Kurtköy-Pendik/İstanbul` — 1 product(s)
- `TÜM EKİP İLAÇ A.Ş., Tuzla/İstanbul` — 1 product(s)
- `VEM İlaç San. ve Tic. A.Ş., Çerkezköy Organize Sanayi Bölgesi, Karaağaç Mah. Fatih Bulv. No:38, Kapaklı/Tekirdağ` — 1 product(s)

## Cross-ingredient resolved facilities

- `FACILITY_YENIBOSNA_SANAYI13_001`: 2 products; 2 active ingredients (famotidin, pantoprazol)

## Modeling rule

Facility resolution establishes an entity-level link only. It does not establish that the observed facility is the sole approved site, that the site performs a particular mandatory role, or that loss of the facility necessarily disables the product.

