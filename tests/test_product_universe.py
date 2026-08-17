from openpyxl import Workbook

from pharma_resilience.product_universe import (
    AliasEntry,
    IngredientMatch,
    locate_header_row,
    map_core_columns,
    match_seed_ingredients,
    normalize_text,
    tokenize,
)


def _alias(
    family,
    canonical,
    alias,
):
    return AliasEntry(
        family_id=family,
        canonical_ingredient=canonical,
        alias=alias,
        alias_type="test",
        notes="",
        tokens=tokenize(alias),
    )


def test_normalize_text_handles_turkish_and_punctuation():
    assert (
        normalize_text("  ETKİN   MADDE / ÇÖZÜCÜ ")
        == "etkin madde cozucu"
    )


def test_phrase_safe_matching_blocks_citalopram_collision():
    registry = (
        _alias(
            "FAM_SSRI",
            "citalopram",
            "citalopram",
        ),
        _alias(
            "FAM_SSRI",
            "escitalopram",
            "escitalopram",
        ),
    )

    result = match_seed_ingredients(
        "ESCİTALOPRAM OKSALAT",
        registry,
    )

    assert [
        x.canonical_ingredient
        for x in result
    ] == ["escitalopram"]


def test_phrase_safe_matching_blocks_loratadine_collision():
    registry = (
        _alias(
            "FAM_H1_ANTIHISTAMINE",
            "loratadine",
            "loratadine",
        ),
        _alias(
            "FAM_H1_ANTIHISTAMINE",
            "desloratadine",
            "desloratadine",
        ),
    )

    result = match_seed_ingredients(
        "DESLORATADINE",
        registry,
    )

    assert [
        x.canonical_ingredient
        for x in result
    ] == ["desloratadine"]


def test_multiple_aliases_same_canonical_collapse():
    registry = (
        _alias(
            "FAM_STATINS",
            "atorvastatin",
            "atorvastatin",
        ),
        _alias(
            "FAM_STATINS",
            "atorvastatin",
            "atorvastatin calcium",
        ),
    )

    result = match_seed_ingredients(
        "ATORVASTATİN CALCIUM",
        registry,
    )

    assert len(result) == 1

    assert result[0].canonical_ingredient == "atorvastatin"

    assert set(result[0].matched_aliases) == {
        "atorvastatin",
        "atorvastatin calcium",
    }


def test_multiple_distinct_seed_ingredients_are_not_silently_collapsed():
    registry = (
        _alias(
            "FAM_ARB",
            "valsartan",
            "valsartan",
        ),
        _alias(
            "FAM_DPP4",
            "sitagliptin",
            "sitagliptin",
        ),
    )

    result = match_seed_ingredients(
        "VALSARTAN + SITAGLIPTIN",
        registry,
    )

    assert len(result) == 2


def test_header_row_is_detected_below_title_row():
    wb = Workbook()
    ws = wb.active

    ws.append(
        ["RUHSATLI BEŞERİ TIBBİ ÜRÜNLER LİSTESİ"]
    )

    ws.append(
        [
            "SIRA NO",
            "BARKOD",
            "ÜRÜN ADI",
            "ETKİN MADDE",
            "ATC KODU",
            "RUHSAT SAHİBİ",
            "RUHSAT TARİHİ",
            "RUHSAT NUMARASI",
        ]
    )

    ws.append(
        [
            1,
            "123",
            "TEST",
            "ATORVASTATİN",
            "C10AA05",
            "TEST FİRMA",
            "2026-01-01",
            "1/1",
        ]
    )

    header_row = locate_header_row(ws)

    assert header_row == 2

    mapping = map_core_columns(
        ws,
        header_row,
    )

    assert mapping["SIRA NO"] == 1
    assert mapping["BARKOD"] == 2
    assert mapping["ÜRÜN ADI"] == 3
    assert mapping["ETKİN MADDE"] == 4
    assert mapping["ATC KODU"] == 5
    assert mapping["RUHSAT SAHİBİ"] == 6
    assert mapping["RUHSAT TARİHİ"] == 7
    assert mapping["RUHSAT NUMARASI"] == 8



def test_atc_consistency_accepts_expected_family_prefix():
    from pharma_resilience.product_universe import (
        classify_seeded_record,
        load_alias_registry,
    )

    registry = load_alias_registry(
        "data/manual/ingredient_aliases_v0_1.csv"
    )

    status, matches = classify_seeded_record(
        "atorvastatin",
        "C10AA05",
        registry,
    )

    assert status == "ATC_CONSISTENT"
    assert len(matches) == 1


def test_atc_consistency_rejects_unexpected_prefix():
    from pharma_resilience.product_universe import (
        classify_seeded_record,
        load_alias_registry,
    )

    registry = load_alias_registry(
        "data/manual/ingredient_aliases_v0_1.csv"
    )

    status, matches = classify_seeded_record(
        "atorvastatin",
        "C09CA01",
        registry,
    )

    assert status == "UNEXPECTED_ATC"
    assert len(matches) == 1


def test_atc_consistency_keeps_missing_atc_for_review():
    from pharma_resilience.product_universe import (
        classify_seeded_record,
        load_alias_registry,
    )

    registry = load_alias_registry(
        "data/manual/ingredient_aliases_v0_1.csv"
    )

    status, matches = classify_seeded_record(
        "atorvastatin",
        "",
        registry,
    )

    assert status == "MISSING_ATC"
    assert len(matches) == 1


def test_multiple_seed_match_is_reviewed_before_atc_decision():
    from pharma_resilience.product_universe import (
        classify_seeded_record,
        load_alias_registry,
    )

    registry = load_alias_registry(
        "data/manual/ingredient_aliases_v0_1.csv"
    )

    status, matches = classify_seeded_record(
        "olanzapin ve fluoksetin",
        "N05AH",
        registry,
    )

    assert status == "MULTIPLE_SEED_MATCH"
    assert len(matches) == 2




# --- licence-level eligibility tests ---

from types import SimpleNamespace

from pharma_resilience.product_universe import (
    collapse_licence_suspension_states,
    evaluate_family_eligibility,
)


def _licence_row(
    licence,
    family,
    suspension,
):
    return SimpleNamespace(
        licence_number=licence,
        family_id=family,
        suspension_status=suspension,
    )


def _eligibility_row(
    licence,
    family,
    state="ALL_ACTIVE",
):
    return SimpleNamespace(
        licence_number=licence,
        family_id=family,
        licence_state=state,
    )


def test_collapse_same_active_licence_presentations():
    rows = [
        _licence_row(
            "2020/1",
            "FAM_TEST",
            "0",
        ),
        _licence_row(
            "2020/1",
            "FAM_TEST",
            "0",
        ),
    ]

    result = collapse_licence_suspension_states(rows)

    assert list(result) == ["2020/1"]
    assert result["2020/1"]["state"] == "ALL_ACTIVE"
    assert result["2020/1"]["presentation_count"] == 2
    assert result["2020/1"]["families"] == ("FAM_TEST",)


def test_collapse_all_suspended_licence():
    rows = [
        _licence_row(
            "2020/2",
            "FAM_TEST",
            "1",
        ),
        _licence_row(
            "2020/2",
            "FAM_TEST",
            "1",
        ),
    ]

    result = collapse_licence_suspension_states(rows)

    assert result["2020/2"]["state"] == "ALL_SUSPENDED"


def test_collapse_mixed_licence_is_not_silently_resolved():
    rows = [
        _licence_row(
            "2020/3",
            "FAM_TEST",
            "0",
        ),
        _licence_row(
            "2020/3",
            "FAM_TEST",
            "1",
        ),
    ]

    result = collapse_licence_suspension_states(rows)

    assert result["2020/3"]["state"] == "MIXED"


def test_family_eligibility_collapses_duplicate_presentations():
    rows = []

    for i in range(1, 7):
        rows.append(
            _eligibility_row(
                f"2020/{i}",
                "FAM_PASS",
            )
        )

    # Same licence repeated as another presentation:
    rows.append(
        _eligibility_row(
            "2020/1",
            "FAM_PASS",
        )
    )

    result = evaluate_family_eligibility(rows)

    assert result["FAM_PASS"]["eligible_products"] == 6
    assert result["FAM_PASS"]["distinct_active_licences"] == 6
    assert result["FAM_PASS"]["eligible"] is True


def test_product_and_licence_thresholds_are_reported_separately():
    rows = [
        _eligibility_row(
            f"2030/{i}",
            "FAM_THRESHOLD",
        )
        for i in range(1, 6)
    ]

    result = evaluate_family_eligibility(
        rows,
        min_products=6,
        min_active_licences=4,
    )

    x = result["FAM_THRESHOLD"]

    assert x["eligible_products"] == 5
    assert x["distinct_active_licences"] == 5
    assert x["passes_product_threshold"] is False
    assert x["passes_licence_threshold"] is True
    assert x["eligible"] is False


def test_suspended_licence_is_excluded_from_eligibility():
    rows = [
        _eligibility_row(
            "2040/1",
            "FAM_TEST",
            "ALL_ACTIVE",
        ),
        _eligibility_row(
            "2040/2",
            "FAM_TEST",
            "ALL_SUSPENDED",
        ),
    ]

    result = evaluate_family_eligibility(
        rows,
        min_products=1,
        min_active_licences=1,
    )

    assert result["FAM_TEST"]["eligible_products"] == 1
    assert result["FAM_TEST"]["distinct_active_licences"] == 1
    assert result["FAM_TEST"]["eligible"] is True
