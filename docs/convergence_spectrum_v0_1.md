# Dependency Convergence Spectrum v0.1

Exhaustive node-level scan of the frozen observed pharmaceutical dependency graph.

> Cross-ingredient convergence is descriptive. It is not evidence of mandatory dependence or common-mode failure.

## Graph coverage

- Products: **9**
- Dependency nodes scanned: **21**
- Non-placeholder nodes: **19**
- Placeholder nodes: **2**
- Shared non-placeholder nodes: **2**
- Informative cross-ingredient nodes: **2**

## By dependency type

| Type | Nodes | Non-placeholder | Shared | Cross-ingredient |
|---|---:|---:|---:|---:|
| `closure` | 6 | 4 | 0 | 0 |
| `container` | 4 | 4 | 1 | 1 |
| `process` | 2 | 2 | 1 | 1 |
| `site` | 9 | 9 | 0 | 0 |

## Informative cross-ingredient nodes

| Node | Type | Products | Active ingredients | Ingredients |
|---|---|---:|---:|---|
| `process::lyophilized` | `process` | 7 | 4 | esomeprazol, famotidin, omeprazol, pantoprazol |
| `container::type_I_clear_glass_vial` | `container` | 5 | 3 | esomeprazol, omeprazol, pantoprazol |

## Interpretation

Because every dependency node is evaluated under the same pre-specified rule, nodes reported above are not manually selected examples from the graph.

Placeholder observations such as `unknown` and `not_applicable...` are retained for auditability but excluded from substantive convergence counts.

