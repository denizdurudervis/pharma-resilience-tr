from pharma_resilience.route_robustness import (
    expected_routes_remaining,
    targeted_routes_remaining,
    gap_is_informative,
)


def test_three_singleton_routes_are_noninformative():
    r = ["A", "B", "C"]
    assert expected_routes_remaining(r, 1) == 1
    assert expected_routes_remaining(r, 2) == 2
    assert expected_routes_remaining(r, 3) == 3
    assert targeted_routes_remaining(r, 1) == 1
    assert targeted_routes_remaining(r, 2) == 2
    assert targeted_routes_remaining(r, 3) == 3
    assert gap_is_informative(r) is False


def test_repeated_route_makes_gap_potentially_informative():
    r = ["A", "A", "B"]
    assert gap_is_informative(r) is True
