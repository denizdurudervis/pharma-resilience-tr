from __future__ import annotations

import csv
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


UNKNOWN = "unknown"


def _clean(value):
    value = "" if value is None else str(value).strip()
    return value if value else UNKNOWN


def _entropy(values):
    values = list(values)
    n = len(values)
    if n == 0:
        return 0.0

    counts = Counter(values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def conditional_entropy(pairs):
    """
    pairs = [(form, signature), ...]
    Returns H(S), H(S|F), I(S;F).
    """
    pairs = [(_clean(f), _clean(s)) for f, s in pairs]

    if not pairs:
        return {
            "h_signature": 0.0,
            "h_signature_given_form": 0.0,
            "mutual_information": 0.0,
            "n": 0,
        }

    signatures = [s for _, s in pairs]
    h_signature = _entropy(signatures)

    by_form = defaultdict(list)
    for form, signature in pairs:
        by_form[form].append(signature)

    n = len(pairs)
    h_cond = 0.0

    for values in by_form.values():
        weight = len(values) / n
        h_cond += weight * _entropy(values)

    mi = h_signature - h_cond

    return {
        "h_signature": h_signature,
        "h_signature_given_form": h_cond,
        "mutual_information": max(0.0, mi),
        "n": n,
    }


def signature_is_function_of_form(pairs):
    """
    True iff every observed form maps to exactly one signature.
    """
    mapping = defaultdict(set)

    for form, signature in pairs:
        mapping[_clean(form)].add(_clean(signature))

    return bool(mapping) and all(len(signatures) == 1 for signatures in mapping.values())


def stratum_table(pairs):
    """
    Form-level diagnostic table.
    """
    by_form = defaultdict(list)

    for form, signature in pairs:
        by_form[_clean(form)].append(_clean(signature))

    rows = []

    for form in sorted(by_form):
        signatures = by_form[form]
        rows.append(
            {
                "form": form,
                "n_products": len(signatures),
                "n_distinct_signatures": len(set(signatures)),
                "evaluable": len(signatures) >= 2,
            }
        )

    return rows


def _permutation_null(pairs, n_perm, seed):
    rng = random.Random(seed)

    forms = [f for f, _ in pairs]
    signatures = [s for _, s in pairs]

    observed = conditional_entropy(pairs)["h_signature_given_form"]

    null_values = []

    for _ in range(n_perm):
        shuffled = signatures[:]
        rng.shuffle(shuffled)

        null_pairs = list(zip(forms, shuffled))
        null_values.append(
            conditional_entropy(null_pairs)["h_signature_given_form"]
        )

    if not null_values:
        return {
            "n_perm": 0,
            "null_mean": None,
            "null_sd": None,
            "share_null_le_obs": None,
            "observed": observed,
        }

    mean = sum(null_values) / len(null_values)

    if len(null_values) > 1:
        variance = sum((x - mean) ** 2 for x in null_values) / (
            len(null_values) - 1
        )
        sd = math.sqrt(variance)
    else:
        sd = 0.0

    share = sum(x <= observed for x in null_values) / len(null_values)

    return {
        "n_perm": len(null_values),
        "null_mean": mean,
        "null_sd": sd,
        "share_null_le_obs": share,
        "observed": observed,
    }


def gate_a(rows, residual_threshold=0.25, n_perm=200, seed=20260817):
    """
    Gate A:
    Does pharmaceutical form determine the observed component signature?

    Signature = normalized (container_class, closure_class).

    The primary diagnostic is normalized residual entropy:

        H(S|F) / H(S)

    A low residual means form explains most of the signature variation.
    """

    pairs = []

    for row in rows:
        form = _clean(row.get("pharmaceutical_form"))
        container = _clean(row.get("container_class"))
        closure = _clean(row.get("closure_class"))

        signature = f"{container}|{closure}"
        pairs.append((form, signature))

    entropy = conditional_entropy(pairs)
    table = stratum_table(pairs)

    evaluable = [r for r in table if r["evaluable"]]

    # Not evaluable when there is no within-form replication.
    if len(evaluable) == 0:
        return {
            "verdict": "not_evaluable",
            "reason": "No pharmaceutical-form stratum contains at least two products.",
            "n_products": len(pairs),
            "n_evaluable_strata": 0,
            "entropy": entropy,
            "residual_entropy_ratio": None,
            "signature_determined_by_form": signature_is_function_of_form(pairs),
            "strata": table,
            "permutation_null": None,
        }

    # If there is no signature variation anywhere, there is nothing to test.
    if entropy["h_signature"] <= 1e-12:
        return {
            "verdict": "not_evaluable",
            "reason": "Only one component signature is observed across all products.",
            "n_products": len(pairs),
            "n_evaluable_strata": len(evaluable),
            "entropy": entropy,
            "residual_entropy_ratio": 0.0,
            "signature_determined_by_form": True,
            "strata": table,
            "permutation_null": None,
        }

    residual = (
        entropy["h_signature_given_form"]
        / entropy["h_signature"]
    )

    null = _permutation_null(pairs, n_perm=n_perm, seed=seed)

    determined = signature_is_function_of_form(pairs)

    if determined or residual <= residual_threshold:
        verdict = "fail"
    else:
        verdict = "pass"

    return {
        "verdict": verdict,
        "reason": (
            "Observed component signature is largely determined by "
            "pharmaceutical form."
            if verdict == "fail"
            else
            "Within-form component variation remains after conditioning on form."
        ),
        "n_products": len(pairs),
        "n_evaluable_strata": len(evaluable),
        "entropy": entropy,
        "residual_entropy_ratio": residual,
        "signature_determined_by_form": determined,
        "strata": table,
        "permutation_null": null,
        "threshold": residual_threshold,
    }


def load_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--threshold", type=float, default=0.25)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--json-out", default=None)

    args = parser.parse_args()

    rows = load_csv(args.csv_path)
    result = gate_a(
        rows,
        residual_threshold=args.threshold,
        n_perm=args.n_perm,
    )

    print("GATE A — COMPONENT DISCRIMINATIVENESS")
    print()
    print("rows =", len(rows))
    print("verdict =", result["verdict"])
    print("evaluable strata =", result["n_evaluable_strata"])
    print(
        "signature determined by form =",
        result["signature_determined_by_form"],
    )

    print()
    print("entropy =", result["entropy"])

    if result["residual_entropy_ratio"] is not None:
        print(
            "normalized residual H(S|F)/H(S) =",
            round(result["residual_entropy_ratio"], 6),
        )

    print()
    print("STRATA")

    for row in result["strata"]:
        print(
            row["form"],
            "| n =",
            row["n_products"],
            "| distinct signatures =",
            row["n_distinct_signatures"],
            "| evaluable =",
            row["evaluable"],
        )

    if result["permutation_null"] is not None:
        print()
        print("PERMUTATION NULL")
        print(result["permutation_null"])

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print()
        print("JSON written to", out)


if __name__ == "__main__":
    main()
