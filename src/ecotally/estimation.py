"""Sampling completeness and richness estimation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import comb, isfinite
from typing import Iterable


@dataclass(frozen=True)
class RichnessEstimate:
    """Observed and extrapolated richness for count data."""

    observed_richness: int
    chao1_richness: float
    sample_coverage: float
    singletons: int
    doubletons: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def _counts(abundances: Iterable[float]) -> list[int]:
    values = list(abundances)
    if not values:
        raise ValueError("at least one abundance is required")
    counts: list[int] = []
    for abundance in values:
        value = float(abundance)
        if value < 0 or not isfinite(value) or not value.is_integer():
            raise ValueError("richness estimation requires non-negative integer counts")
        counts.append(int(value))
    if sum(counts) == 0:
        raise ValueError("total abundance must be greater than zero")
    return counts


def estimate_richness(abundances: Iterable[float]) -> RichnessEstimate:
    """Estimate unseen richness using bias-corrected Chao1.

    Sample coverage is the Good estimator ``1 - f1 / N``.
    """

    counts = _counts(abundances)
    positive = [count for count in counts if count > 0]
    singletons = positive.count(1)
    doubletons = positive.count(2)
    observed = len(positive)
    chao1 = observed + singletons * (singletons - 1) / (2 * (doubletons + 1))
    coverage = max(0.0, 1.0 - singletons / sum(positive))
    return RichnessEstimate(observed, chao1, coverage, singletons, doubletons)


def expected_richness(abundances: Iterable[float], sample_size: int) -> float:
    """Expected species richness after rarefaction to ``sample_size``."""

    counts = _counts(abundances)
    total = sum(counts)
    if sample_size < 1 or sample_size > total:
        raise ValueError(f"sample_size must be between 1 and {total}")
    denominator = comb(total, sample_size)
    return sum(
        1.0
        - (
            comb(total - count, sample_size) / denominator
            if total - count >= sample_size
            else 0.0
        )
        for count in counts
        if count > 0
    )


def rarefaction_curve(
    abundances: Iterable[float], *, points: int = 20
) -> list[dict[str, float | int]]:
    """Return an evenly spaced individual-based rarefaction curve."""

    counts = _counts(abundances)
    if points < 2:
        raise ValueError("points must be at least 2")
    total = sum(counts)
    sizes = {1, total}
    sizes.update(round(1 + index * (total - 1) / (points - 1)) for index in range(points))
    return [
        {"sample_size": size, "expected_richness": expected_richness(counts, size)}
        for size in sorted(sizes)
    ]
