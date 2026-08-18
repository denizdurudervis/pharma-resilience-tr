from pharma_resilience.presentation_form import (
    UNKNOWN_FORM,
    classify_pharmaceutical_form,
    normalize_product_name,
)


def test_turkish_unicode_normalization():
    raw = "D\u0130AZEM \u015eURUP \u00c7\u00d6ZELT\u0130"

    assert (
        normalize_product_name(raw)
        == "DIAZEM SURUP COZELTI"
    )


def test_syrup():
    assert classify_pharmaceutical_form(
        "DESLORAN \u015eURUP, 150 ML"
    ) == "syrup"


def test_injection_solution():
    assert classify_pharmaceutical_form(
        "DOREN 15 MG/3 ML "
        "ENJEKS\u0130YONLUK "
        "\u00c7\u00d6ZELT\u0130"
    ) == "injection_solution"


def test_infusion_typo_variant():
    assert classify_pharmaceutical_form(
        "ACLABON INFIZYON COZELTISI "
        "ICEREN FLAKON"
    ) == "infusion_solution"


def test_infusion_concentrate_long_wording():
    assert classify_pharmaceutical_form(
        "ZOLDRIA 4MG 5ML INFUZYON "
        "ICIN KONSANTRE ICEREN FLAKON"
    ) == "infusion_concentrate"


def test_infusion_concentrate_abbreviation():
    assert classify_pharmaceutical_form(
        "ZOMEBON 4 MG/5ML IV INF. "
        "ICIN KON.COZELTI ICEREN "
        "KUL.HAZIR SIRINGA"
    ) == "infusion_concentrate"


def test_long_acting_injection_suspension():
    assert classify_pharmaceutical_form(
        "TREVICTA 175 MG IM "
        "ENJEKSIYON ICIN UZUN "
        "SALIMLI SUSPANSIYON"
    ) == "injection_suspension"


def test_odt_wording():
    assert classify_pharmaceutical_form(
        "OFANS ODT 5 MG AGIZDA DAGILAN"
    ) == "orodispersible_tablet"


def test_film_kapli_tb():
    assert classify_pharmaceutical_form(
        "LOSANEW-100-MG-FILM-KAPLI-TB"
    ) == "film_coated_tablet"


def test_ftb():
    assert classify_pharmaceutical_form(
        "TAMGARD 80 MG 28 FTB"
    ) == "film_coated_tablet"


def test_sachet_alone_remains_unknown():
    assert classify_pharmaceutical_form(
        "FIXBONE 150 MG SASE, 3 ADET"
    ) == UNKNOWN_FORM


def test_ampoule_alone_remains_unknown():
    assert classify_pharmaceutical_form(
        "ZOLTEM 2ML 4 MG 1 AMPUL"
    ) == UNKNOWN_FORM


def test_cartridge_autoinjector_remains_unknown():
    assert classify_pharmaceutical_form(
        "IMIGRAN SUBJECT 6MG/0,5ML "
        "2 KARTUS + OTOENJEKTOR"
    ) == UNKNOWN_FORM



def test_reconcile_single_known_form():
    from pharma_resilience.presentation_form import (
        reconcile_licence_forms,
    )

    assert reconcile_licence_forms(
        ["capsule"]
    ) == "capsule"


def test_reconcile_unknown_only():
    from pharma_resilience.presentation_form import (
        UNKNOWN_FORM,
        reconcile_licence_forms,
    )

    assert reconcile_licence_forms(
        [UNKNOWN_FORM, UNKNOWN_FORM]
    ) == UNKNOWN_FORM


def test_reconcile_generic_tablet_with_film_coated():
    from pharma_resilience.presentation_form import (
        reconcile_licence_forms,
    )

    assert reconcile_licence_forms(
        [
            "tablet",
            "film_coated_tablet",
        ]
    ) == "film_coated_tablet"


def test_reconcile_generic_tablet_with_orodispersible():
    from pharma_resilience.presentation_form import (
        reconcile_licence_forms,
    )

    assert reconcile_licence_forms(
        [
            "tablet",
            "orodispersible_tablet",
        ]
    ) == "orodispersible_tablet"


def test_reconcile_true_conflict_is_not_silently_resolved():
    from pharma_resilience.presentation_form import (
        reconcile_licence_forms,
    )

    assert reconcile_licence_forms(
        [
            "capsule",
            "film_coated_tablet",
        ]
    ) is None
