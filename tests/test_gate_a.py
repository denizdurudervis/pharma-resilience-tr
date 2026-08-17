from pharma_resilience.gate_a import (
    conditional_entropy,
    gate_a,
    signature_is_function_of_form,
    stratum_table,
)


def _row(form, process, container, closure):
    return {
        "pharmaceutical_form": form,
        "process_class": process,
        "container_class": container,
        "closure_class": closure,
    }


def test_form_determines_signature_is_a_fail():
    rows = [
        _row("powder for solution", "lyophilized",
             "type_I_clear_glass_vial", "bromobutyl_stopper"),
        _row("powder for solution", "lyophilized",
             "type_I_clear_glass_vial", "bromobutyl_stopper"),
        _row("solution", "aseptic_liquid_fill",
             "type_I_glass_ampoule", "none"),
        _row("solution", "aseptic_liquid_fill",
             "type_I_glass_ampoule", "none"),
    ]

    res = gate_a(rows, n_perm=200)

    assert res["signature_determined_by_form"] is True
    assert res["verdict"] == "fail"


def test_variation_within_form_can_pass():
    rows = [
        _row("powder for solution", "lyophilized",
             "type_I_clear_glass_vial", "bromobutyl_stopper"),
        _row("powder for solution", "lyophilized",
             "type_I_glass_ampoule", "fused_seal"),
        _row("powder for solution", "lyophilized",
             "hdpe_bottle", "screw_cap"),
        _row("solution", "aseptic_liquid_fill",
             "type_I_glass_ampoule", "fused_seal"),
    ]

    res = gate_a(rows, residual_threshold=0.25, n_perm=200)

    assert res["signature_determined_by_form"] is False
    assert res["verdict"] == "pass"


def test_single_signature_everywhere_is_not_evaluable():
    rows = [
        _row("powder for solution", "lyophilized",
             "type_I_clear_glass_vial", "bromobutyl_stopper"),
        _row("solution", "aseptic_liquid_fill",
             "type_I_clear_glass_vial", "bromobutyl_stopper"),
    ]

    res = gate_a(rows, n_perm=200)

    assert res["verdict"] == "not_evaluable"


def test_all_strata_singletons_is_not_evaluable():
    rows = [
        _row("f1", "p1", "c1", "s1"),
        _row("f2", "p2", "c2", "s2"),
        _row("f3", "p3", "c3", "s3"),
    ]

    res = gate_a(rows, n_perm=200)

    assert res["verdict"] == "not_evaluable"
    assert res["n_evaluable_strata"] == 0

def test_unknown_is_kept_as_its_own_level_not_imputed():
    rows = [
        _row(
            "powder for solution",
            "lyophilized",
            "type_I_clear_glass_vial",
            "",
        ),
        _row(
            "powder for solution",
            "lyophilized",
            "type_I_clear_glass_vial",
            "bromobutyl_stopper",
        ),
    ]

    pairs = [
        (
            "powder for solution",
            "type_i_clear_glass_vial|unknown",
        ),
        (
            "powder for solution",
            "type_i_clear_glass_vial|bromobutyl_stopper",
        ),
    ]

    table = stratum_table(pairs)

    assert table[0]["n_distinct_signatures"] == 2
    assert len(table) == 1

    res = gate_a(rows, n_perm=200)

    assert res["entropy"]["h_signature"] > 0

def test_entropy_identities():
    pairs = [
        (("a",), ("x",)),
        (("a",), ("y",)),
        (("b",), ("x",)),
        (("b",), ("x",)),
    ]

    flat = [(f[0], s[0]) for f, s in pairs]

    e = conditional_entropy(flat)

    assert e["mutual_information"] >= -1e-12
    assert e["h_signature_given_form"] <= e["h_signature"] + 1e-12
    assert signature_is_function_of_form(flat) is False
