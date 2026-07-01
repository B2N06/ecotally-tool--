"""Diversity metrics with no runtime dependencies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, log
from typing import Iterable


@dataclass(frozen=True)
class DiversityResult:
    """Common alpha-diversity metrics for one ecological community."""

    total_abundance: float
    richness: int
    shannon: float
    simpson: float
    inverse_simpson: float
    pielou_evenness: float
    hill_q0: float
    hill_q1: float
    hill_q2: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def calculate_diversity(abundances: Iterable[float]) -> DiversityResult:
    """Calculate alpha diversity from non-negative species abundances.

    Zeros are accepted and ignored. Negative, non-finite, or empty-total
    communities are rejected because their ecological interpretation is
    ambiguous.
    """

    values = [float(value) for value in abundances]
    if not values:
        raise ValueError("at least one abundance is required")
    if any(value < 0 for value in values):
        raise ValueError("abundances cannot be negative")
    if any(value == float("inf") or value != value for value in values):
        raise ValueError("abundances must be finite")

    positive = [value for value in values if value > 0]
    total = sum(positive)
    if total <= 0:
        raise ValueError("total abundance must be greater than zero")

    proportions = [value / total for value in positive]
    richness = len(positive)
    shannon = -sum(p * log(p) for p in proportions)
    dominance = sum(p * p for p in proportions)
    simpson = 1.0 - dominance
    inverse_simpson = 1.0 / dominance
    evenness = shannon / log(richness) if richness > 1 else 1.0

    return DiversityResult(
        total_abundance=total,
        richness=richness,
        shannon=shannon,
        simpson=simpson,
        inverse_simpson=inverse_simpson,
        pielou_evenness=evenness,
        hill_q0=float(richness),
        hill_q1=exp(shannon),
        hill_q2=inverse_simpson,
    )


def hill_number(abundances: Iterable[float], order: float) -> float:
    """Calculate a Hill number for any non-negative diversity order."""

    values = [float(value) for value in abundances]
    if order < 0 or order != order or order == float("inf"):
        raise ValueError("Hill order must be finite and non-negative")
    if not values or any(value < 0 for value in values):
        raise ValueError("abundances must be non-empty and non-negative")
    if any(value != value or value == float("inf") for value in values):
        raise ValueError("abundances must be finite")
    positive = [value for value in values if value > 0]
    total = sum(positive)
    if total == 0:
        raise ValueError("total abundance must be greater than zero")
    if order == 0:
        return float(len(positive))
    proportions = [value / total for value in positive]
    if order == 1:
        return exp(-sum(p * log(p) for p in proportions))
    return sum(p**order for p in proportions) ** (1 / (1 - order))
