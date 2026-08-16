import pytest

from pharma_resilience.poc_main_figure import (
    build_plot_payload,
    load_summary,
)


SUMMARY_PATH = (
    "data/processed/"
    "poc_results_summary_v0_1.json"
)


def _payload():
    summary = load_summary(
        SUMMARY_PATH
    )

    return build_plot_payload(
        summary
    )


def test_mean_resolution_trajectory():
    payload = _payload()

    assert payload[
        "mean_documented"
    ] == pytest.approx(
        [
            0.666666,
            0.916666,
            1.0,
        ]
    )

    assert payload[
        "mean_envelope"
    ] == pytest.approx(
        [
            1.388889,
            1.416667,
            1.416667,
        ]
    )


def test_six_pair_trajectories_are_present():
    payload = _payload()

    assert len(
        payload["pair_series"]
    ) == 6


def test_strongest_terminal_pair():
    payload = _payload()

    strongest = payload[
        "pair_series"
    ][0]

    assert strongest[
        "label"
    ] == (
        "esomeprazol – pantoprazol"
    )

    assert strongest[
        "values"
    ] == pytest.approx(
        [
            1.5,
            2.0,
            2.0,
        ]
    )

    assert strongest[
        "resolution_sensitive"
    ] is True

    assert strongest[
        "unresolved_evidence_sensitive"
    ] is False


def test_esomeprazole_omeprazole_trajectory():
    payload = _payload()

    match = next(
        item
        for item in payload[
            "pair_series"
        ]
        if item["label"]
        == "esomeprazol – omeprazol"
    )

    assert match[
        "values"
    ] == pytest.approx(
        [
            0.5,
            1.0,
            1.5,
        ]
    )

    assert match[
        "resolution_sensitive"
    ] is True

    assert match[
        "unresolved_evidence_sensitive"
    ] is True