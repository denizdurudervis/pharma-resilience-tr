from pharma_resilience.mah import mah_statistics, molecule_extinction_cut


def test_mah_basic():
    holder_by_license = {
        "L1": "H1",
        "L2": "H1",
        "L3": "H2",
        "L4": "H3",
    }
    s = mah_statistics(holder_by_license)
    assert s["n_licenses"] == 4
    assert s["n_holders"] == 3
    assert s["max_holder_loss_fraction"] == 0.5


def test_molecule_cut():
    records = [
        {"holder": "A", "molecule": "M1"},
        {"holder": "B", "molecule": "M1"},
        {"holder": "A", "molecule": "M2"},
    ]
    cuts = molecule_extinction_cut(records)
    assert cuts["M1"] == 2
    assert cuts["M2"] == 1
