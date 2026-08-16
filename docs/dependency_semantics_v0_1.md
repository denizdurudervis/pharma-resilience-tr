# Dependency Semantics v0.1

Semantic gate between the observed dependency graph and disruption/interdiction modeling.

> Shared node does not imply shared failure mode.

## Representation classes

- `descriptive_process_class`: **2**
- `observed_site_mention`: **9**
- `physical_component_class`: **10**

## Interdiction readiness

- Dependency nodes: **21**
- Resolved single physical failure entities: **0**
- Product-mandatory dependencies established: **0**
- Direct-interdiction-ready nodes: **0**

## Current modeling rule

Process classes, container classes, and closure classes must not be interpreted as unique physical failure entities.

Named manufacturing-site strings are currently treated only as observed site mentions. Entity normalization is required before determining whether two mentions correspond to the same physical facility.

Even after site entity resolution, current public evidence does not establish site role, mandatory dependence, or exhaustiveness of the approved manufacturing-site set.

Therefore no current dependency node is assumed to disable a product deterministically when removed.

