from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "family_selection_v0_1"

DEFAULT_STUDY_SEED = (
    "pharma_resilience_tr_expansion_v0_1"
)

TARGET_FAMILIES = 8
TARGET_PER_STRATUM = 4
MINIMUM_DESIRED_FAMILIES = 6

ALLOWED_STRATA = {
    "H",
    "D",
}

ALLOWED_STATUSES = {
    "eligible",
    "ineligible",
    "pending",
}


def read_registry(
    path: str | Path,
) -> list[dict[str, str]]:
    with Path(path).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def deterministic_hash(
    family_id: str,
    study_seed: str = DEFAULT_STUDY_SEED,
) -> str:
    """
    Return reproducible SHA-256 selection key.

    Exact frozen input convention:

        study_seed || family_id
    """

    payload = (
        f"{study_seed}||{family_id}"
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


def validate_registry(
    rows: list[dict[str, str]],
) -> None:
    seen_ids: set[str] = set()

    for index, row in enumerate(
        rows,
        start=2,
    ):
        family_id = (
            row.get("family_id") or ""
        ).strip()

        status = (
            row.get("eligibility_status")
            or ""
        ).strip().lower()

        stratum = (
            row.get("route_form_stratum")
            or ""
        ).strip().upper()

        if not family_id:
            raise ValueError(
                f"Missing family_id at CSV line {index}"
            )

        if family_id in seen_ids:
            raise ValueError(
                f"Duplicate family_id: {family_id}"
            )

        seen_ids.add(family_id)

        if status not in ALLOWED_STATUSES:
            raise ValueError(
                f"Invalid eligibility_status for "
                f"{family_id}: {status!r}"
            )

        if status == "eligible":
            if stratum not in ALLOWED_STRATA:
                raise ValueError(
                    f"Eligible family {family_id} "
                    f"must have stratum H or D; "
                    f"observed {stratum!r}"
                )


def _eligible_rows(
    rows: list[dict[str, str]],
    study_seed: str,
) -> list[dict[str, Any]]:
    eligible: list[dict[str, Any]] = []

    for row in rows:
        status = (
            row.get("eligibility_status")
            or ""
        ).strip().lower()

        if status != "eligible":
            continue

        family_id = (
            row.get("family_id") or ""
        ).strip()

        stratum = (
            row.get("route_form_stratum")
            or ""
        ).strip().upper()

        item: dict[str, Any] = {
            key: value
            for key, value in row.items()
        }

        item[
            "route_form_stratum"
        ] = stratum

        item[
            "eligibility_status"
        ] = status

        item[
            "selection_hash"
        ] = deterministic_hash(
            family_id,
            study_seed,
        )

        eligible.append(item)

    eligible.sort(
        key=lambda item: (
            item["selection_hash"],
            item["family_id"],
        )
    )

    return eligible


def select_families(
    rows: list[dict[str, str]],
    study_seed: str = DEFAULT_STUDY_SEED,
    target_families: int = TARGET_FAMILIES,
    target_per_stratum: int = TARGET_PER_STRATUM,
) -> dict[str, Any]:
    """
    Deterministically select eligible therapeutic families.

    Primary allocation:
        up to target_per_stratum from H
        up to target_per_stratum from D

    Remaining target slots are filled from all remaining eligible
    families using the same SHA-256 ordering.

    Packaging/component information is never used.
    """

    validate_registry(rows)

    eligible = _eligible_rows(
        rows,
        study_seed,
    )

    by_stratum = {
        "H": [
            item
            for item in eligible
            if item["route_form_stratum"] == "H"
        ],
        "D": [
            item
            for item in eligible
            if item["route_form_stratum"] == "D"
        ],
    }

    selected: list[dict[str, Any]] = []

    for stratum in (
        "H",
        "D",
    ):
        selected.extend(
            by_stratum[stratum][
                :target_per_stratum
            ]
        )

    selected_ids = {
        item["family_id"]
        for item in selected
    }

    remaining_slots = max(
        0,
        target_families
        - len(selected),
    )

    if remaining_slots:
        remaining = [
            item
            for item in eligible
            if item["family_id"]
            not in selected_ids
        ]

        remaining.sort(
            key=lambda item: (
                item["selection_hash"],
                item["family_id"],
            )
        )

        selected.extend(
            remaining[
                :remaining_slots
            ]
        )

    selected = selected[
        :target_families
    ]

    selected.sort(
        key=lambda item: (
            item["selection_hash"],
            item["family_id"],
        )
    )

    selected_ids = {
        item["family_id"]
        for item in selected
    }

    not_selected = [
        item
        for item in eligible
        if item["family_id"]
        not in selected_ids
    ]

    n_selected_h = sum(
        item["route_form_stratum"] == "H"
        for item in selected
    )

    n_selected_d = sum(
        item["route_form_stratum"] == "D"
        for item in selected
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "study_seed": study_seed,
        "selection_rule": (
            "SHA-256(study_seed || family_id)"
        ),
        "target_families": target_families,
        "target_per_stratum": (
            target_per_stratum
        ),
        "minimum_desired_families": (
            MINIMUM_DESIRED_FAMILIES
        ),
        "registry_counts": {
            "n_registry_rows": len(rows),
            "n_eligible": len(eligible),
            "n_selected": len(selected),
            "n_not_selected_eligible": len(
                not_selected
            ),
            "n_selected_H": n_selected_h,
            "n_selected_D": n_selected_d,
            "minimum_desired_target_met": (
                len(selected)
                >= MINIMUM_DESIRED_FAMILIES
            ),
        },
        "selected_families": selected,
        "eligible_not_selected": (
            not_selected
        ),
    }


def write_selected_csv(
    analysis: dict[str, Any],
    path: str | Path,
) -> None:
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    selected = analysis[
        "selected_families"
    ]

    base_fields = [
        "family_id",
        "family_name",
        "clinical_context",
        "eligibility_basis",
        "evidence_source",
        "route_form_stratum",
        "n_candidate_active_ingredients",
        "n_candidate_products",
        "eligibility_status",
        "exclusion_reason",
        "reviewer_note",
    ]

    fieldnames = (
        base_fields
        + ["selection_hash"]
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for row in selected:
            writer.writerow(row)


def write_json(
    analysis: dict[str, Any],
    path: str | Path,
) -> None:
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            analysis,
            handle,
            ensure_ascii=False,
            indent=2,
        )

        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Deterministically select expanded-sample "
            "therapeutic families from a frozen registry."
        )
    )

    parser.add_argument(
        "registry_csv"
    )

    parser.add_argument(
        "--selected-out",
        default=(
            "data/processed/"
            "selected_families_v0_1.csv"
        ),
    )

    parser.add_argument(
        "--json-out",
        default=(
            "data/processed/"
            "family_selection_v0_1.json"
        ),
    )

    parser.add_argument(
        "--study-seed",
        default=DEFAULT_STUDY_SEED,
    )

    args = parser.parse_args()

    rows = read_registry(
        args.registry_csv
    )

    analysis = select_families(
        rows,
        study_seed=args.study_seed,
    )

    write_selected_csv(
        analysis,
        args.selected_out,
    )

    write_json(
        analysis,
        args.json_out,
    )

    print(
        "DETERMINISTIC FAMILY SELECTION"
    )
    print()

    counts = analysis[
        "registry_counts"
    ]

    print(
        "registry rows =",
        counts["n_registry_rows"],
    )

    print(
        "eligible =",
        counts["n_eligible"],
    )

    print(
        "selected =",
        counts["n_selected"],
    )

    print(
        "selected H =",
        counts["n_selected_H"],
    )

    print(
        "selected D =",
        counts["n_selected_D"],
    )

    print(
        "minimum desired target met =",
        counts[
            "minimum_desired_target_met"
        ],
    )

    print()

    print("SELECTED FAMILIES")

    for item in analysis[
        "selected_families"
    ]:
        print(
            item["family_id"],
            "|",
            item["route_form_stratum"],
            "|",
            item["selection_hash"][:12],
            "|",
            item.get(
                "family_name",
                "",
            ),
        )


if __name__ == "__main__":
    main()