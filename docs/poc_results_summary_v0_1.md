# Pharmaceutical Component-Resilience PoC Results Summary v0.1

## Frozen dataset

- Products: **9**
- Component-audit rows: **19**
- Explicit component observations: **18**
- Unresolved products: **1**
- Unresolved product IDs: `OMHEAL_2025_605`

## Resolution trajectory

| Level | Component classes | Cross-ingredient classes | Mean documented pair overlap | Mean unresolved envelope |
|---|---:|---:|---:|---:|
| `R0_exact` | 9 | 3 | 0.667 | 1.389 |
| `R1_parent` | 6 | 4 | 0.917 | 1.417 |
| `R2_terminal` | 5 | 3 | 1.000 | 1.417 |

## Ingredient-pair trajectories

| Pair | R0 documented | R1 documented | R2 documented | Resolution-sensitive | Unresolved-evidence-sensitive |
|---|---:|---:|---:|---|---|
| esomeprazol – pantoprazol | 1.500 | 2.000 | 2.000 | Yes | No |
| esomeprazol – omeprazol | 0.500 | 1.000 | 1.500 | Yes | Yes |
| omeprazol – pantoprazol | 1.000 | 1.500 | 1.500 | Yes | Yes |
| esomeprazol – famotidin | 0.333 | 0.333 | 0.333 | No | No |
| famotidin – omeprazol | 0.333 | 0.333 | 0.333 | No | Yes |
| famotidin – pantoprazol | 0.333 | 0.333 | 0.333 | No | No |

## PoC findings

- Highest terminal documented-overlap score: **2.000**, observed for **esomeprazol – pantoprazol**.
- Resolution-sensitive ingredient pairs: **3/6**.
- Pairs sensitive to fully unresolved-product evidence: **3/6**.

## Interpretation limits

Observed or evidence-weighted component overlap does not establish supplier identity, mandatory dependence, non-substitutability, common failure mode, disruption probability, or national shortage risk.

The current frozen sample is a proof of concept within a parenteral acid-suppression product family. The observed convergence may therefore partly reflect dosage-form conditioning and must be tested in a pre-specified expanded sample with diversified negative controls.

