from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .audit_summary import read_csv
from .site_entity_resolution import (
    extract_site_mentions,
)


RESOLVED_DECISIONS = {
    "same_entity",
    "same_entity_temporal_alias",
}


TRUE_VALUES = {
    "1",
    "true",
    "yes",
}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _load_products(
    product_csv: str | Path,
) -> dict[str, dict[str, str]]:
    rows = read_csv(product_csv)

    products: dict[
        str,
        dict[str, str],
    ] = {}

    for row in rows:
        product_id = _clean(
            row.get("product_id")
        )

        if not product_id:
            continue

        products[product_id] = {
            "product_id": product_id,
            "product_name": _clean(
                row.get("product_name")
            ),
            "active_ingredient": _clean(
                row.get("active_ingredient")
            ),
        }

    return products


def load_resolution_decisions(
    decisions_csv: str | Path,
) -> list[dict[str, str]]:
    rows = read_csv(decisions_csv)

    required = {
        "left_raw_mention",
        "right_raw_mention",
        "decision",
        "resolved_entity_id",
    }

    if rows:
        missing = required - set(
            rows[0].keys()
        )

        if missing:
            raise ValueError(
                "Resolution decision table is missing "
                f"required fields: {sorted(missing)}"
            )

    return rows


def build_resolution_map(
    decisions: list[dict[str, str]],
) -> tuple[
    dict[str, str],
    dict[str, list[dict[str, str]]],
]:
    raw_to_entity: dict[
        str,
        str,
    ] = {}

    entity_decisions: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    for row in decisions:
        left = _clean(
            row.get("left_raw_mention")
        )

        right = _clean(
            row.get("right_raw_mention")
        )

        decision = _clean(
            row.get("decision")
        )

        entity_id = _clean(
            row.get("resolved_entity_id")
        )

        if decision in RESOLVED_DECISIONS:
            if not entity_id:
                raise ValueError(
                    "Resolved decision requires a "
                    "resolved_entity_id."
                )

            for raw_mention in {
                left,
                right,
            }:
                if not raw_mention:
                    continue

                existing = raw_to_entity.get(
                    raw_mention
                )

                if (
                    existing is not None
                    and existing != entity_id
                ):
                    raise ValueError(
                        "A raw site mention maps to "
                        "multiple resolved entities: "
                        f"{raw_mention!r}"
                    )

                raw_to_entity[
                    raw_mention
                ] = entity_id

            entity_decisions[
                entity_id
            ].append(
                dict(row)
            )

        elif decision == "unresolved":
            if entity_id:
                raise ValueError(
                    "Unresolved decision must not contain "
                    "a resolved_entity_id."
                )

        else:
            raise ValueError(
                f"Unknown resolution decision: "
                f"{decision!r}"
            )

    return (
        raw_to_entity,
        dict(entity_decisions),
    )


def _extract_product_site_observations(
    evidence_csv: str | Path,
) -> list[dict[str, str]]:
    rows = read_csv(evidence_csv)

    observations: list[
        dict[str, str]
    ] = []

    seen: set[
        tuple[str, str]
    ] = set()

    for row in rows:
        if (
            _clean(row.get("field_name"))
            != "manufacturing_site"
        ):
            continue

        field_present = _clean(
            row.get("field_present")
        ).casefold()

        if field_present not in TRUE_VALUES:
            continue

        product_id = _clean(
            row.get("product_id")
        )

        raw_mention = _clean(
            row.get("observed_value")
        )

        if not product_id or not raw_mention:
            continue

        pair = (
            product_id,
            raw_mention,
        )

        if pair in seen:
            continue

        seen.add(pair)

        observations.append(
            {
                "product_id": product_id,
                "raw_site_mention": raw_mention,
            }
        )

    return observations


def build_resolved_site_graph(
    product_csv: str | Path,
    evidence_csv: str | Path,
    decisions_csv: str | Path,
) -> dict[str, Any]:
    products = _load_products(
        product_csv
    )

    site_mentions = extract_site_mentions(
        evidence_csv
    )

    decisions = load_resolution_decisions(
        decisions_csv
    )

    (
        raw_to_entity,
        entity_decisions,
    ) = build_resolution_map(
        decisions
    )

    observations = (
        _extract_product_site_observations(
            evidence_csv
        )
    )

    resolved_entities: dict[
        str,
        dict[str, Any],
    ] = {}

    unresolved_mentions: dict[
        str,
        dict[str, Any],
    ] = {}

    product_targets: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    for observation in observations:
        product_id = observation[
            "product_id"
        ]

        raw_mention = observation[
            "raw_site_mention"
        ]

        product = products.get(
            product_id,
            {
                "product_id": product_id,
                "product_name": "",
                "active_ingredient": "",
            },
        )

        entity_id = raw_to_entity.get(
            raw_mention
        )

        if entity_id:
            if entity_id not in resolved_entities:
                resolved_entities[
                    entity_id
                ] = {
                    "resolved_entity_id": entity_id,
                    "raw_mentions": set(),
                    "product_ids": set(),
                    "active_ingredients": set(),
                    "product_names": set(),
                    "decision_types": set(),
                    "confidence_values": set(),
                    "evidence_bases": set(),
                }

            entity = resolved_entities[
                entity_id
            ]

            entity[
                "raw_mentions"
            ].add(raw_mention)

            entity[
                "product_ids"
            ].add(product_id)

            if product[
                "active_ingredient"
            ]:
                entity[
                    "active_ingredients"
                ].add(
                    product[
                        "active_ingredient"
                    ]
                )

            if product[
                "product_name"
            ]:
                entity[
                    "product_names"
                ].add(
                    product[
                        "product_name"
                    ]
                )

            product_targets[
                product_id
            ].append(
                {
                    "target_kind": (
                        "resolved_facility"
                    ),
                    "target_id": entity_id,
                    "raw_site_mention": (
                        raw_mention
                    ),
                }
            )

        else:
            if raw_mention not in unresolved_mentions:
                mention_info = site_mentions.get(
                    raw_mention,
                    {
                        "normalized_text": "",
                        "company_prefix_key": "",
                        "product_ids": [],
                    },
                )

                unresolved_mentions[
                    raw_mention
                ] = {
                    "raw_site_mention": raw_mention,
                    "normalized_text": (
                        mention_info.get(
                            "normalized_text",
                            "",
                        )
                    ),
                    "company_prefix_key": (
                        mention_info.get(
                            "company_prefix_key",
                            "",
                        )
                    ),
                    "product_ids": set(),
                    "active_ingredients": set(),
                    "product_names": set(),
                }

            mention = unresolved_mentions[
                raw_mention
            ]

            mention[
                "product_ids"
            ].add(product_id)

            if product[
                "active_ingredient"
            ]:
                mention[
                    "active_ingredients"
                ].add(
                    product[
                        "active_ingredient"
                    ]
                )

            if product[
                "product_name"
            ]:
                mention[
                    "product_names"
                ].add(
                    product[
                        "product_name"
                    ]
                )

            product_targets[
                product_id
            ].append(
                {
                    "target_kind": (
                        "unresolved_site_mention"
                    ),
                    "target_id": raw_mention,
                    "raw_site_mention": (
                        raw_mention
                    ),
                }
            )

    for entity_id, rows in (
        entity_decisions.items()
    ):
        entity = resolved_entities.setdefault(
            entity_id,
            {
                "resolved_entity_id": entity_id,
                "raw_mentions": set(),
                "product_ids": set(),
                "active_ingredients": set(),
                "product_names": set(),
                "decision_types": set(),
                "confidence_values": set(),
                "evidence_bases": set(),
            },
        )

        for row in rows:
            entity[
                "decision_types"
            ].add(
                _clean(
                    row.get("decision")
                )
            )

            confidence = _clean(
                row.get("confidence")
            )

            if confidence:
                entity[
                    "confidence_values"
                ].add(confidence)

            evidence_basis = _clean(
                row.get("evidence_basis")
            )

            if evidence_basis:
                entity[
                    "evidence_bases"
                ].add(
                    evidence_basis
                )

            for field in (
                "left_raw_mention",
                "right_raw_mention",
            ):
                raw_mention = _clean(
                    row.get(field)
                )

                if raw_mention:
                    entity[
                        "raw_mentions"
                    ].add(raw_mention)

    resolved_output: dict[
        str,
        dict[str, Any],
    ] = {}

    for entity_id, entity in sorted(
        resolved_entities.items()
    ):
        resolved_output[
            entity_id
        ] = {
            "resolved_entity_id": entity_id,
            "raw_mentions": sorted(
                entity["raw_mentions"]
            ),
            "n_raw_mentions": len(
                entity["raw_mentions"]
            ),
            "product_ids": sorted(
                entity["product_ids"]
            ),
            "n_products": len(
                entity["product_ids"]
            ),
            "product_names": sorted(
                entity["product_names"]
            ),
            "active_ingredients": sorted(
                entity[
                    "active_ingredients"
                ]
            ),
            "n_active_ingredients": len(
                entity[
                    "active_ingredients"
                ]
            ),
            "decision_types": sorted(
                entity[
                    "decision_types"
                ]
            ),
            "confidence_values": sorted(
                entity[
                    "confidence_values"
                ]
            ),
            "evidence_bases": sorted(
                entity[
                    "evidence_bases"
                ]
            ),
            "single_failure_entity": True,
            "mandatory_product_dependency_established": False,
            "direct_interdiction_ready": False,
        }

    unresolved_output: dict[
        str,
        dict[str, Any],
    ] = {}

    for raw_mention, values in sorted(
        unresolved_mentions.items()
    ):
        unresolved_output[
            raw_mention
        ] = {
            "raw_site_mention": raw_mention,
            "normalized_text": values[
                "normalized_text"
            ],
            "company_prefix_key": values[
                "company_prefix_key"
            ],
            "product_ids": sorted(
                values["product_ids"]
            ),
            "n_products": len(
                values["product_ids"]
            ),
            "product_names": sorted(
                values["product_names"]
            ),
            "active_ingredients": sorted(
                values[
                    "active_ingredients"
                ]
            ),
            "n_active_ingredients": len(
                values[
                    "active_ingredients"
                ]
            ),
            "single_failure_entity": False,
            "mandatory_product_dependency_established": False,
            "direct_interdiction_ready": False,
        }

    cross_ingredient_resolved = {
        entity_id: values
        for entity_id, values
        in resolved_output.items()
        if values[
            "n_active_ingredients"
        ] >= 2
    }

    products_with_resolved = {
        product_id
        for entity
        in resolved_output.values()
        for product_id
        in entity["product_ids"]
    }

    products_with_unresolved = {
        product_id
        for mention
        in unresolved_output.values()
        for product_id
        in mention["product_ids"]
    }

    return {
        "n_products": len(products),
        "n_raw_site_mentions": len(
            site_mentions
        ),
        "n_site_observations": len(
            observations
        ),
        "n_resolved_facility_entities": len(
            resolved_output
        ),
        "n_resolved_raw_mentions": len(
            raw_to_entity
        ),
        "n_unresolved_raw_mentions": len(
            unresolved_output
        ),
        "n_products_with_resolved_facility": len(
            products_with_resolved
        ),
        "n_products_with_unresolved_site_mention": len(
            products_with_unresolved
        ),
        "n_cross_ingredient_resolved_facilities": len(
            cross_ingredient_resolved
        ),
        "resolved_entities": (
            resolved_output
        ),
        "unresolved_mentions": (
            unresolved_output
        ),
        "cross_ingredient_resolved_facilities": (
            cross_ingredient_resolved
        ),
        "product_site_targets": {
            product_id: targets
            for product_id, targets
            in sorted(
                product_targets.items()
            )
        },
        "interpretation": (
            "Resolved facility entities are created only "
            "from manually adjudicated same-entity decisions. "
            "Unresolved site mentions remain separate. "
            "A resolved physical facility is not automatically "
            "a mandatory product dependency and is therefore "
            "not yet direct-interdiction-ready."
        ),
    }


def render_markdown(
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []

    lines.append(
        "# Resolved Site Graph v0.1"
    )
    lines.append("")

    lines.append(
        "Application of manually audited site-entity "
        "resolution decisions to the frozen product sample."
    )
    lines.append("")

    lines.append(
        "> Resolved facility identity does not establish "
        "mandatory product dependence."
    )
    lines.append("")

    lines.append("## Resolution summary")
    lines.append("")

    lines.append(
        f"- Raw site mentions: "
        f"**{summary['n_raw_site_mentions']}**"
    )

    lines.append(
        f"- Site observations: "
        f"**{summary['n_site_observations']}**"
    )

    lines.append(
        "- Resolved facility entities: "
        f"**{summary['n_resolved_facility_entities']}**"
    )

    lines.append(
        "- Raw mentions assigned to resolved facilities: "
        f"**{summary['n_resolved_raw_mentions']}**"
    )

    lines.append(
        "- Unresolved raw site mentions: "
        f"**{summary['n_unresolved_raw_mentions']}**"
    )

    lines.append(
        "- Cross-ingredient resolved facilities: "
        f"**{summary['n_cross_ingredient_resolved_facilities']}**"
    )

    lines.append("")
    lines.append(
        "## Resolved facilities"
    )
    lines.append("")

    if not summary[
        "resolved_entities"
    ]:
        lines.append(
            "No manually resolved facility entities."
        )
    else:
        lines.append(
            "| Facility | Raw mentions | Products | "
            "Active ingredients | Ingredients | "
            "Interdiction ready? |"
        )

        lines.append(
            "|---|---:|---:|---:|---|---|"
        )

        for entity_id, values in summary[
            "resolved_entities"
        ].items():
            ingredients = ", ".join(
                values[
                    "active_ingredients"
                ]
            )

            lines.append(
                f"| `{entity_id}` | "
                f"{values['n_raw_mentions']} | "
                f"{values['n_products']} | "
                f"{values['n_active_ingredients']} | "
                f"{ingredients} | "
                f"{values['direct_interdiction_ready']} |"
            )

    lines.append("")
    lines.append(
        "## Unresolved site mentions"
    )
    lines.append("")

    if not summary[
        "unresolved_mentions"
    ]:
        lines.append(
            "No unresolved site mentions."
        )
    else:
        for raw_mention, values in summary[
            "unresolved_mentions"
        ].items():
            lines.append(
                f"- `{raw_mention}` — "
                f"{values['n_products']} product(s)"
            )

    lines.append("")
    lines.append(
        "## Cross-ingredient resolved facilities"
    )
    lines.append("")

    cross = summary[
        "cross_ingredient_resolved_facilities"
    ]

    if not cross:
        lines.append(
            "No manually resolved facility is observed "
            "across multiple active ingredients."
        )
    else:
        for entity_id, values in cross.items():
            lines.append(
                f"- `{entity_id}`: "
                f"{values['n_products']} products; "
                f"{values['n_active_ingredients']} active "
                f"ingredients "
                f"({', '.join(values['active_ingredients'])})"
            )

    lines.append("")
    lines.append("## Modeling rule")
    lines.append("")

    lines.append(
        "Facility resolution establishes an entity-level "
        "link only. It does not establish that the observed "
        "facility is the sole approved site, that the site "
        "performs a particular mandatory role, or that loss "
        "of the facility necessarily disables the product."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Apply audited site-resolution decisions "
            "to the pharmaceutical product-site graph."
        )
    )

    parser.add_argument(
        "product_csv"
    )

    parser.add_argument(
        "evidence_csv"
    )

    parser.add_argument(
        "decisions_csv"
    )

    parser.add_argument(
        "--json-out"
    )

    parser.add_argument(
        "--md-out"
    )

    args = parser.parse_args()

    summary = build_resolved_site_graph(
        args.product_csv,
        args.evidence_csv,
        args.decisions_csv,
    )

    markdown = render_markdown(
        summary
    )

    print(markdown)

    if args.json_out:
        output = Path(
            args.json_out
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            json.dumps(
                summary,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    if args.md_out:
        output = Path(
            args.md_out
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            markdown + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()