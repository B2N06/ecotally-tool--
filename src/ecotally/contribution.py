"""Local and species contributions to beta diversity."""

from __future__ import annotations

import random
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


def lcbd_significance(
    communities: Mapping[str, Mapping[str, float]],
    *,
    permutations: int = 999,
    seed: int | None = 0,
) -> list[dict[str, str | float | int]]:
    """Test LCBD with independent column permutations of Hellinger profiles."""

    if permutations < 10:
        raise ValueError("permutations must be at least 10")
    non_empty = {
        site: {species: float(value) for species, value in community.items()}
        for site, community in communities.items()
        if sum(float(value) for value in community.values()) > 0
    }
    if not non_empty:
        raise ValueError("at least one non-empty site is required")
    if any(
        value < 0 or not isfinite(value)
        for community in non_empty.values()
        for value in community.values()
    ):
        raise ValueError("abundances must be finite and non-negative")
    sites = sorted(non_empty)
    species = sorted(
        {
            name
            for community in non_empty.values()
            for name, value in community.items()
            if value > 0
        }
    )
    matrix = []
    for site in sites:
        total = sum(non_empty[site].values())
        matrix.append(
            [sqrt(non_empty[site].get(name, 0.0) / total) for name in species]
        )

    def contributions(values: list[list[float]]) -> list[float]:
        means = [
            sum(row[index] for row in values) / len(values)
            for index in range(len(species))
        ]
        row_ss = [
            sum(
                (row[index] - means[index]) ** 2
                for index in range(len(species))
            )
            for row in values
        ]
        total_ss = sum(row_ss)
        return [value / total_ss if total_ss > 0 else 0.0 for value in row_ss]

    observed = contributions(matrix)
    exceedances = [0] * len(sites)
    rng = random.Random(seed)
    for _ in range(permutations):
        permuted = [[0.0] * len(species) for _ in sites]
        for column in range(len(species)):
            values = [row[column] for row in matrix]
            rng.shuffle(values)
            for row_index, value in enumerate(values):
                permuted[row_index][column] = value
        for index, value in enumerate(contributions(permuted)):
            if value + 1e-12 >= observed[index]:
                exceedances[index] += 1
    return [
        {
            "site": site,
            "lcbd": observed[index],
            "p_value": (exceedances[index] + 1) / (permutations + 1),
            "permutations": permutations,
        }
        for index, site in enumerate(sites)
    ]
