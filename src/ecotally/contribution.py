"""Local and species contributions to beta diversity."""

from __future__ import annotations

from math import isfinite, sqrt
from typing import Mapping


def beta_contributions(
    communities: Mapping[str, Mapping[str, float]],
) -> dict[str, list[dict[str, str | float]]]:
    """Partition Hellinger variance into LCBD and SCBD contributions."""

    non_empty: dict[str, dict[str, float]] = {}
    for site, community in communities.items():
        cleaned: dict[str, float] = {}
        for species, abundance in community.items():
            value = float(abundance)
            if value < 0 or not isfinite(value):
                raise ValueError("abundances must be finite and non-negative")
            cleaned[species] = value
        if sum(cleaned.values()) > 0:
            non_empty[site] = cleaned
    if not non_empty:
        raise ValueError("at least one non-empty site is required")

    sites = sorted(non_empty)
    species = sorted(
        {
            name
            for community in non_empty.values()
            for name, abundance in community.items()
            if abundance > 0
        }
    )
    matrix: list[list[float]] = []
    for site in sites:
        total = sum(non_empty[site].values())
        matrix.append(
            [sqrt(non_empty[site].get(name, 0.0) / total) for name in species]
        )
    column_means = [
        sum(row[index] for row in matrix) / len(matrix)
        for index in range(len(species))
    ]
    squared = [
        [
            (row[index] - column_means[index]) ** 2
            for index in range(len(species))
        ]
        for row in matrix
    ]
    site_ss = [sum(row) for row in squared]
    species_ss = [
        sum(row[index] for row in squared) for index in range(len(species))
    ]
    total_ss = sum(site_ss)
    return {
        "lcbd": [
            {"site": site, "lcbd": value / total_ss if total_ss > 0 else 0.0}
            for site, value in zip(sites, site_ss)
        ],
        "scbd": [
            {"species": name, "scbd": value / total_ss if total_ss > 0 else 0.0}
            for name, value in zip(species, species_ss)
        ],
    }
