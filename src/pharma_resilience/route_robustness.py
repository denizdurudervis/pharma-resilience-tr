from collections import Counter
from math import comb


def expected_routes_remaining(route_labels: list[str], k: int) -> float:
    """
    Exact Hurlbert-style expectation:
    expected number of distinct routes represented among k surviving products.
    Here it is interpreted as a random product-failure baseline, not as an
    ecological sampling correction.
    """
    n = len(route_labels)
    if not 0 <= k <= n:
        raise ValueError("k must satisfy 0 <= k <= N")
    if k == 0:
        return 0.0
    counts = Counter(route_labels)
    denom = comb(n, k)
    total = 0.0
    for nr in counts.values():
        absent = comb(n - nr, k) / denom if n - nr >= k else 0.0
        total += 1.0 - absent
    return total


def targeted_routes_remaining(route_labels: list[str], k: int) -> int:
    """
    Closed form for the partition case: each product belongs to one
    route-signature class and route classes are disjoint.
    """
    n = len(route_labels)
    if not 0 <= k <= n:
        raise ValueError("k must satisfy 0 <= k <= N")
    counts = sorted(Counter(route_labels).values())
    removals = n - k
    destroyed = 0
    spent = 0
    for c in counts:
        if spent + c <= removals:
            spent += c
            destroyed += 1
        else:
            break
    return len(counts) - destroyed


def gap_is_informative(route_labels: list[str]) -> bool:
    counts = Counter(route_labels)
    return bool(counts) and max(counts.values()) >= 2
