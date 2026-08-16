from pathlib import Path

from pharma_resilience.family_checkpoint import summarize_family


DATA = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "manual"
    / "product_audit_v0_1.csv"
)


def test_frozen_famotidine_checkpoint():
    summary = summarize_family(DATA, "famotidin")

    assert summary["n_products"] == 3
    assert summary["n_process_classes"] == 2
    assert summary["n_route_signatures"] == 3

    assert summary["process_counts"] == {
        "liquid": 1,
        "lyophilized": 2,
    }

    assert summary["route_counts"] == {
        "liquid|ampoule": 1,
        "lyophilized|vial+solvent_ampoule": 1,
        "lyophilized|ampoule+solvent_ampoule": 1,
    }

    assert summary["max_route_multiplicity"] == 1
    assert summary["robustness_gap_evaluable"] is False

    assert summary["process_container_counts"] == {
        ("liquid", "ampoule"): 1,
        ("lyophilized", "vial"): 1,
        ("lyophilized", "ampoule"): 1,
    }

    assert summary["random_curve"] == [
        (1, 1.0),
        (2, 2.0),
        (3, 3.0),
    ]

    assert summary["targeted_curve"] == [
        (1, 1),
        (2, 2),
        (3, 3),
    ]