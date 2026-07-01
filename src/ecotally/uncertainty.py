"""Reproducible bootstrap uncertainty for count-based diversity metrics."""

from __future__ import annotations

import random
from math import isfinite
from typing import Iterable

from .diversity import calculate_diversity


def _percentile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def bootstrap_diversity(
    abundances: Iterable[float],
    *,
    replicates: int = 999,
    confidence: float = 0.95,
    seed: int | None = 0,
) -> dict[str, dict[str, float]]:
    """Estimate percentile intervals by resampling observed individuals."""

    counts: list[int] = []
    for abundance in abundances:
        value = float(abundance)
        if value < 0 or not isfinite(value) or not value.is_integer():
            raise ValueError("bootstrap requires non-negative integer counts")
        counts.append(int(value))
    total = sum(counts)
    if total == 0:
        raise ValueError("total abundance must be greater than zero")
    if replicates < 10:
        raise ValueError("replicates must be at least 10")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    population = [
        species_index
        for species_index, count in enumerate(counts)
        for _ in range(count)
    ]
    rng = random.Random(seed)
    metrics = ("richness", "shannon", "simpson", "pielou_evenness")
    samples: dict[str, list[float]] = {metric: [] for metric in metrics}
    for _ in range(replicates):
        replicate_counts = [0] * len(counts)
        for species_index in rng.choices(population, k=total):
            replicate_counts[species_index] += 1
        result = calculate_diversity(replicate_counts)
        for metric in metrics:
            samples[metric].append(float(getattr(result, metric)))

    estimate = calculate_diversity(counts)
    tail = (1 - confidence) / 2
    return {
        metric: {
            "estimate": float(getattr(estimate, metric)),
            "lower": _percentile(sorted(samples[metric]), tail),
            "upper": _percentile(sorted(samples[metric]), 1 - tail),
        }
        for metric in metrics
    }
