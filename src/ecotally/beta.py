"""Pairwise beta-diversity measures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class PairwiseResult:
    """Dissimilarity between two communities, ranging from zero to one."""

    jaccard_dissimilarity: float
    sorensen_dissimilarity: float
    bray_curtis_dissimilarity: float
    shared_species: int
    unique_to_first: int
    unique_to_second: int

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def _validated(community: Mapping[str, float]) -> dict[str, float]:
    result: dict[str, float] = {}
    for species, abundance in community.items():
        value = float(abundance)
        if not species:
            raise ValueError("species names cannot be empty")
        if value < 0 or not isfinite(value):
            raise ValueError("abundances must be finite and non-negative")
        result[species] = value
    return result


def compare_communities(
    first: Mapping[str, float], second: Mapping[str, float]
) -> PairwiseResult:
    """Calculate incidence- and abundance-based pairwise dissimilarity."""

    a, b = _validated(first), _validated(second)
    species = set(a) | set(b)
    if not species or sum(a.values()) + sum(b.values()) == 0:
        raise ValueError("at least one community must have positive abundance")

    present_a = {name for name, value in a.items() if value > 0}
    present_b = {name for name, value in b.items() if value > 0}
    union = present_a | present_b
    shared = present_a & present_b
    jaccard = 1.0 - (len(shared) / len(union)) if union else 0.0
    sorensen = 1.0 - (
        2 * len(shared) / (len(present_a) + len(present_b))
        if present_a or present_b
        else 0.0
    )

    numerator = sum(abs(a.get(name, 0.0) - b.get(name, 0.0)) for name in species)
    denominator = sum(a.get(name, 0.0) + b.get(name, 0.0) for name in species)
    bray_curtis = numerator / denominator

    return PairwiseResult(
        jaccard,
        sorensen,
        bray_curtis,
        len(shared),
        len(present_a - present_b),
        len(present_b - present_a),
    )
