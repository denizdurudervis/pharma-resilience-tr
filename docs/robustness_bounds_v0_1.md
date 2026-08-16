# Facility Robustness Bounds v0.1

Evidence-bounded disruption analysis for manually resolved manufacturing facilities.

> Bounds represent what current public evidence can and cannot exclude; they are not estimated failure probabilities.

## Summary

- Resolved facilities: **2**
- Facilities with non-zero uncertainty gap: **2**
- Possible cross-ingredient facility impacts: **1**
- Certain cross-ingredient facility impacts: **0**
- Maximum possible affected products from one resolved facility: **2**
- Maximum possible active-ingredient span from one resolved facility: **2**

## Facility bounds

| Facility | Product impact | Ingredient impact | Possible cross-ingredient? |
|---|---:|---:|---|
| `FACILITY_VEM_KAPAKLI_001` | 0–1 | 0–1 | False |
| `FACILITY_YENIBOSNA_SANAYI13_001` | 0–2 | 0–2 | True |

## Interpretation

A non-zero upper bound does not establish that facility loss would disable the associated products. It means that the available public evidence does not exclude mandatory dependence.

A zero lower bound reflects absence of proven mandatory dependence rather than evidence of operational redundancy.

