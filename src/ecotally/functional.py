"""Trait-based functional diversity."""

from __future__ import annotations

from dataclasses import dataclass
from math import dist, isfinite
from typing import Mapping


@dataclass(frozen=True)
class FunctionalResult:
    """Functional diversity for one abundance-weighted community."""

    trait_coverage: float
    functional_dispersion: float
    rao_q: float
    community_weighted_means: dict[str, float]

    def to_rows(self, site: str) -> list[dict[str, str | float]]:
        rows: list[dict[str, str | float]] = [
            {"site": site, "metric": "trait_coverage", "value": self.trait_coverage},
            {
                "site": site,
                "metric": "functional_dispersion",
                "value": self.functional_dispersion,
            },
            {"site": site, "metric": "rao_q", "value": self.rao_q},
        ]
        rows.extend(
            {
                "site": site,
                "metric": "community_weighted_mean",
                "trait": trait,
                "value": value,
            }
            for trait, value in self.community_weighted_means.items()
        )
        return rows


def calculate_functional_diversity(
    community: Mapping[str, float],
    traits: Mapping[str, Mapping[str, float]],
) -> FunctionalResult:
    """Calculate abundance-weighted FDis, Rao's Q, and trait means.

    Euclidean distances are used, so callers should standardize traits when
    their units or scales differ substantially.
    """

    total_abundance = sum(float(value) for value in community.values())
    if total_abundance <= 0:
        raise ValueError("community must have positive total abundance")
    available = [
        species
        for species, abundance in community.items()
        if abundance > 0 and species in traits
    ]
    if not available:
        raise ValueError("no observed species have trait data")
    trait_names = list(next(iter(traits.values())).keys())
    if not trait_names:
        raise ValueError("at least one trait is required")
    for species, values in traits.items():
        if set(values) != set(trait_names):
            raise ValueError(f"inconsistent trait columns for '{species}'")
        if any(not isfinite(float(value)) for value in values.values()):
            raise ValueError("trait values must be finite")

    covered_total = sum(float(community[species]) for species in available)
    weights = {
        species: float(community[species]) / covered_total for species in available
    }
    vectors = {
        species: [float(traits[species][trait]) for trait in trait_names]
        for species in available
    }
    centroid = [
        sum(weights[species] * vectors[species][index] for species in available)
        for index in range(len(trait_names))
    ]
    dispersion = sum(
        weights[species] * dist(vectors[species], centroid)
        for species in available
    )
    rao_q = sum(
        weights[first] * weights[second] * dist(vectors[first], vectors[second])
        for first in available
        for second in available
    )
    means = {
        trait: sum(
            weights[species] * float(traits[species][trait])
            for species in available
        )
        for trait in trait_names
    }
    return FunctionalResult(
        covered_total / total_abundance,
        dispersion,
        rao_q,
        means,
    )
