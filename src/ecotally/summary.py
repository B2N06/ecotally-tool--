"""Dataset-scale community summaries."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Mapping


Community = Mapping[str, float]


@dataclass(frozen=True)
class DatasetSummary:
    """Alpha, beta, and gamma structure across sampled sites."""

    site_count: int
    gamma_richness: int
    mean_alpha_richness: float
    whittaker_beta: float
    total_abundance: float

    def to_dict(self) -> dict[str, float | int]:
        return asdict(self)


def _validated(
    communities: Mapping[str, Community],
) -> dict[str, dict[str, float]]:
    if not communities:
        raise ValueError("at least one community is required")
    result: dict[str, dict[str, float]] = {}
    for site, community in communities.items():
        if not site:
            raise ValueError("site names cannot be empty")
        cleaned: dict[str, float] = {}
        for species, abundance in community.items():
            value = float(abundance)
            if not species:
                raise ValueError("species names cannot be empty")
            if value < 0 or not isfinite(value):
                raise ValueError("abundances must be finite and non-negative")
            cleaned[species] = value
        result[site] = cleaned
    return result


def summarize_dataset(
    communities: Mapping[str, Community],
) -> DatasetSummary:
    """Summarize richness partitioning across sites."""

    data = _validated(communities)
    richness = [
        sum(abundance > 0 for abundance in community.values())
        for community in data.values()
    ]
    mean_alpha = sum(richness) / len(richness)
    present = {
        species
        for community in data.values()
        for species, abundance in community.items()
        if abundance > 0
    }
    gamma = len(present)
    beta = gamma / mean_alpha if mean_alpha else 0.0
    total = sum(sum(community.values()) for community in data.values())
    return DatasetSummary(len(data), gamma, mean_alpha, beta, total)


def summarize_species(
    communities: Mapping[str, Community],
) -> list[dict[str, str | float | int]]:
    """Return occupancy and abundance for every observed species."""

    data = _validated(communities)
    site_count = len(data)
    species_names = sorted(
        {
            species
            for community in data.values()
            for species, abundance in community.items()
            if abundance > 0
        }
    )
    rows: list[dict[str, str | float | int]] = []
    for species in species_names:
        occupied = sum(community.get(species, 0.0) > 0 for community in data.values())
        total = sum(community.get(species, 0.0) for community in data.values())
        rows.append(
            {
                "species": species,
                "occupied_sites": occupied,
                "occupancy": occupied / site_count,
                "total_abundance": total,
            }
        )
    return rows
