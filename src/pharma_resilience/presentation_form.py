from __future__ import annotations

import unicodedata


UNKNOWN_FORM = "unknown_form"


def normalize_product_name(value: object) -> str:
    text = str(value or "").strip().upper()

    # Turkish dotted/dotless I.
    text = text.replace("\u0130", "I")
    text = text.replace("\u0131", "I")

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )

    return " ".join(text.split())


def _tokens(value: object) -> set[str]:
    text = normalize_product_name(value)

    for ch in ",;/()+:":
        text = text.replace(ch, " ")

    text = text.replace("-", " ")

    return set(text.split())


def classify_pharmaceutical_form(value: object) -> str:
    text = normalize_product_name(value)
    tok = _tokens(value)

    # ---------------------------------------------------------
    # Parenteral forms
    # ---------------------------------------------------------

    if "LIYOFILIZE" in text:
        return "lyophilized_powder"

    if (
        "ENJEKSIYON" in text
        and "SUSPANSIYON" in text
    ):
        return "injection_suspension"

    if (
        "REKTAL" in text
        and (
            "COZ" in text
            or "SOLUSYON" in text
        )
    ):
        return "rectal_solution"

    infusion_marker = (
        "INFUZYON" in text
        or "INFIZYON" in text
        or "IV INF." in text
    )

    concentrate_marker = (
        "KONSANTRE" in text
        or "KON.COZ" in text
        or "KON. COZ" in text
    )

    if infusion_marker and concentrate_marker:
        return "infusion_concentrate"

    if (
        "ENJEKSIYON" in text
        and concentrate_marker
    ):
        return "injection_concentrate"

    if (
        (
            "ENJEKSIYON" in text
            or "ENJEKTABL" in text
        )
        and (
            "COZ" in text
            or "SOLUSYON" in text
        )
    ):
        return "injection_solution"

    if (
        infusion_marker
        and (
            "COZ" in text
            or "SOLUSYON" in text
        )
    ):
        return "infusion_solution"

    # ---------------------------------------------------------
    # Tablet forms
    # ---------------------------------------------------------

    if "ENTERIK KAPLI TABLET" in text:
        return "enteric_coated_tablet"

    if (
        "UZATILMIS SALIMLI TABLET" in text
        or "KONTROLLU SALIMLI TABLET" in text
    ):
        return "modified_release_tablet"

    if "EFERVESAN TABLET" in text:
        return "effervescent_tablet"

    if (
        "AGIZDA DAGILAN" in text
        or "ODT" in tok
    ):
        return "orodispersible_tablet"

    if "DILALTI TABLET" in text:
        return "sublingual_tablet"

    if (
        "FILM KAPLI TABLET" in text
        or "FILM KAPLI TB" in
            normalize_product_name(value).replace("-", " ")
        or "FTB" in tok
    ):
        return "film_coated_tablet"

    # ---------------------------------------------------------
    # Oral / other explicit forms
    # ---------------------------------------------------------

    if "ORAL SUSPANSIYON" in text:
        return "oral_suspension"

    if "ORAL COZELTI" in text:
        return "oral_solution"

    if "ORAL DAMLA" in text:
        return "oral_drops"

    if "DAMLA" in text:
        return "drops"

    if "SUSPANSIYON" in text:
        return "suspension"

    if "NAZAL SPREY" in text:
        return "nasal_spray"

    if "ORAL SPREY" in text:
        return "oral_spray"

    if "TRANSDERMAL" in text:
        return "transdermal_patch"

    if "SUPPOZITUVAR" in text:
        return "suppository"

    if "REKTAL TUP" in text:
        return "rectal_tube"

    if "DRAJE" in text:
        return "dragee"

    if "SURUP" in text:
        return "syrup"

    if "KAPSUL" in text:
        return "capsule"

    if "TABLET" in text:
        return "tablet"

    # Deliberately NOT used as pharmaceutical-form evidence:
    #
    # AMPUL
    # FLAKON
    # SASE
    # KARTUS
    # ENJEKTOR
    #
    # These describe container/package/device information.

    return UNKNOWN_FORM


# ---------------------------------------------------------------------
# Licence-level form reconciliation
# ---------------------------------------------------------------------

_FORM_REFINEMENTS = {
    "film_coated_tablet": {"tablet"},
    "enteric_coated_tablet": {"tablet"},
    "modified_release_tablet": {"tablet"},
    "effervescent_tablet": {"tablet"},
    "orodispersible_tablet": {"tablet"},
    "sublingual_tablet": {"tablet"},
}


def reconcile_licence_forms(forms):
    """
    Reconcile known pharmaceutical forms observed across multiple
    presentation rows belonging to the same licence.

    Generic + deterministic refinement is collapsed to the more
    specific form.

    Genuine incompatible forms are not silently resolved.

    Returns
    -------
    str | None
        Resolved form, UNKNOWN_FORM when no known form exists,
        or None when a genuine unresolved conflict remains.
    """

    known = {
        str(x).strip()
        for x in forms
        if str(x or "").strip()
        and str(x).strip() != UNKNOWN_FORM
    }

    if not known:
        return UNKNOWN_FORM

    if len(known) == 1:
        return next(iter(known))

    # Remove generic parent forms when their specific refinement
    # is also present.
    reduced = set(known)

    for specific, parents in _FORM_REFINEMENTS.items():
        if specific in reduced:
            reduced.difference_update(
                parent
                for parent in parents
                if parent in reduced
            )

    if len(reduced) == 1:
        return next(iter(reduced))

    return None
