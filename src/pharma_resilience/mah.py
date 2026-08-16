from collections import Counter
from math import inf


def mah_statistics(holder_by_license: dict[str, str]) -> dict:
    counts = Counter(holder_by_license.values())
    n = sum(counts.values())
    if n == 0:
        return {
            "n_licenses": 0,
            "n_holders": 0,
            "hhi_license_share": None,
            "n_eff_holders": None,
            "max_holder_loss_fraction": None,
        }

    hhi = sum((c / n) ** 2 for c in counts.values())
    return {
        "n_licenses": n,
        "n_holders": len(counts),
        "holder_counts": dict(counts),
        "hhi_license_share": hhi,
        "n_eff_holders": 1 / hhi,
        "max_holder_loss_fraction": max(counts.values()) / n,
    }


def molecule_extinction_cut(records: list[dict]) -> dict[str, int]:
    """
    records require: holder, molecule.
    Minimum number of distinct MAHs that must disappear
    to eliminate all licences of each molecule.
    """
    mol_to_holders = {}
    for r in records:
        mol_to_holders.setdefault(r["molecule"], set()).add(r["holder"])
    return {m: len(hs) for m, hs in mol_to_holders.items()}


def family_extinction_cut(records: list[dict]) -> int:
    return len({r["holder"] for r in records})
