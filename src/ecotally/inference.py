"""Small, reproducible randomization tests for ecological comparisons."""

from __future__ import annotations

import random
from math import isfinite
from typing import Mapping


def permutation_group_difference(
    values_by_site: Mapping[str, float],
    group_by_site: Mapping[str, str],
    *,
    metric: str,
    permutations: int = 999,
    seed: int | None = 0,
) -> dict[str, str | float | int]:
    """Compare means of exactly two groups using a two-sided label permutation."""

    if permutations < 10:
        raise ValueError("permutations must be at least 10")
    records = [
        (site, float(value), group_by_site[site])
        for site, value in values_by_site.items()
        if site in group_by_site and group_by_site[site]
    ]
    if any(not isfinite(value) for _, value, _ in records):
        raise ValueError("group comparison values must be finite")
    groups = sorted({group for _, _, group in records})
    if len(groups) != 2:
        raise ValueError("group comparison requires exactly two non-empty groups")
    first, second = groups
    first_values = [value for _, value, group in records if group == first]
    second_values = [value for _, value, group in records if group == second]
    if not first_values or not second_values:
        raise ValueError("both groups must contain at least one site")
    first_mean = sum(first_values) / len(first_values)
    second_mean = sum(second_values) / len(second_values)
    observed = second_mean - first_mean

    values = [value for _, value, _ in records]
    first_size = len(first_values)
    rng = random.Random(seed)
    exceedances = 0
    for _ in range(permutations):
        shuffled = values.copy()
        rng.shuffle(shuffled)
        permuted_first = shuffled[:first_size]
        permuted_second = shuffled[first_size:]
        difference = (
            sum(permuted_second) / len(permuted_second)
            - sum(permuted_first) / len(permuted_first)
        )
        if abs(difference) + 1e-12 >= abs(observed):
            exceedances += 1
    return {
        "metric": metric,
        "group_a": first,
        "group_b": second,
        "mean_a": first_mean,
        "mean_b": second_mean,
        "difference_b_minus_a": observed,
        "p_value": (exceedances + 1) / (permutations + 1),
        "permutations": permutations,
    }
