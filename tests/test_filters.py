from pharma_resilience.filters import is_parenteral_name, fuzzy_active_ingredient_review


def test_iv_boundary_does_not_match_pantactive():
    assert is_parenteral_name("PANTACTIVE 40 MG") is False


def test_iv_boundary_matches_iv_product():
    assert is_parenteral_name("ZYGOX 40 MG I.V.") is True


def test_pantopr_root_flags_typo_for_manual_review():
    hits = fuzzy_active_ingredient_review("pantoprolin")
    assert any(h["root"] == "pantopr" for h in hits)
