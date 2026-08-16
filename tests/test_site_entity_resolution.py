import csv

from pharma_resilience.site_entity_resolution import (
    compare_site_mentions,
    extract_site_mentions,
    generate_site_candidates,
    normalize_site_text,
)


def _write_csv(
    path,
    rows,
):
    fieldnames = [
        "product_id",
        "field_name",
        "field_present",
        "observed_value",
    ]

    with open(
        path,
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(
            rows
        )


def test_normalization_handles_turkish_characters():
    result = normalize_site_text(
        "İLAÇ San. A.Ş."
    )

    assert result == "ilac san a s"


def test_same_company_prefix_generates_candidate():
    left = {
        "raw_mention": (
            "Mefar İlaç San. A.Ş."
        ),
        "normalized_text": (
            "mefar ilac san a s"
        ),
        "company_prefix_key": (
            "mefar ilac san a s"
        ),
        "product_ids": ["p1"],
    }

    right = {
        "raw_mention": (
            "Mefar İlaç San. A.Ş., "
            "Ramazanoğlu Mah. Ensar Cad."
        ),
        "normalized_text": (
            "mefar ilac san a s "
            "ramazanoglu mah ensar cad"
        ),
        "company_prefix_key": (
            "mefar ilac san a s"
        ),
        "product_ids": ["p2"],
    }

    result = compare_site_mentions(
        left,
        right,
    )

    assert result is not None

    assert (
        result["candidate_reason"]
        == "same_company_prefix"
    )

    assert (
        result["decision"]
        == "review_required"
    )


def test_distinct_mentions_are_not_forced_to_match():
    left = {
        "raw_mention": "Company Alpha",
        "normalized_text": "company alpha",
        "company_prefix_key": "company alpha",
        "product_ids": ["p1"],
    }

    right = {
        "raw_mention": "Company Omega",
        "normalized_text": "company omega",
        "company_prefix_key": "company omega",
        "product_ids": ["p2"],
    }

    result = compare_site_mentions(
        left,
        right,
    )

    assert result is None


def test_candidate_generation_never_auto_merges(
    tmp_path,
):
    evidence_path = (
        tmp_path / "evidence.csv"
    )

    _write_csv(
        evidence_path,
        [
            {
                "product_id": "p1",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": (
                    "Mefar İlaç San. A.Ş."
                ),
            },
            {
                "product_id": "p2",
                "field_name": "manufacturing_site",
                "field_present": "1",
                "observed_value": (
                    "Mefar İlaç San. A.Ş., "
                    "Ramazanoğlu Mah. Ensar Cad."
                ),
            },
        ],
    )

    summary = generate_site_candidates(
        evidence_path
    )

    assert (
        summary["n_unique_raw_mentions"]
        == 2
    )

    assert (
        summary["n_candidate_pairs"]
        == 1
    )

    assert (
        summary["n_resolved_entities"]
        == 0
    )

    assert (
        summary["auto_merge_performed"]
        is False
    )

    assert all(
        candidate["decision"]
        == "review_required"
        for candidate
        in summary["candidate_pairs"]
    )