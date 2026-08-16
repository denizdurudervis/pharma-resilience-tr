# Product–Dependency Graph v0.1

Observed dependency graph for the frozen pharmaceutical audit sample.

Unknown dependency attributes are omitted from the graph rather than represented by a shared unknown node.

## Graph size

- Product nodes: **9**
- Dependency nodes: **21**
- Observed edges: **31**

## Dependency nodes by type

- `closure`: 6
- `container`: 4
- `process`: 2
- `site`: 9

## Missing dependency observations

- `closure`: 3 products
- `container`: 1 products
- `process`: 1 products
- `site`: 1 products

## Cross-ingredient shared dependencies

| Type | Dependency | Products | Active ingredients | Ingredients |
|---|---|---:|---:|---|
| `container` | `type_I_clear_glass_vial` | 5 | 3 | esomeprazol, omeprazol, pantoprazol |
| `process` | `lyophilized` | 7 | 4 | esomeprazol, famotidin, omeprazol, pantoprazol |

