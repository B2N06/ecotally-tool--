"""Read ecological observations from simple, interoperable files."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


def read_long_csv(
    path: str | Path,
    *,
    site_column: str = "site",
    species_column: str = "species",
    abundance_column: str = "abundance",
) -> dict[str, dict[str, float]]:
    """Read a long-form CSV and combine duplicate site/species rows."""

    communities: defaultdict[str, defaultdict[str, float]] = defaultdict(
        lambda: defaultdict(float)
    )
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {site_column, species_column, abundance_column}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing CSV columns: {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):
            site = (row[site_column] or "").strip()
            species = (row[species_column] or "").strip()
            if not site or not species:
                raise ValueError(f"line {line_number}: site and species are required")
            try:
                abundance = float(row[abundance_column])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"line {line_number}: abundance must be numeric"
                ) from exc
            if abundance < 0 or abundance != abundance or abundance == float("inf"):
                raise ValueError(
                    f"line {line_number}: abundance must be finite and non-negative"
                )
            communities[site][species] += abundance

    if not communities:
        raise ValueError("CSV contains no observations")
    return {site: dict(species) for site, species in communities.items()}


def read_wide_csv(
    path: str | Path, *, site_column: str = "site"
) -> dict[str, dict[str, float]]:
    """Read a matrix-style CSV with sites in rows and species in columns."""

    communities: dict[str, dict[str, float]] = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if site_column not in headers:
            raise ValueError(f"missing CSV column: {site_column}")
        species_columns = [column for column in headers if column != site_column]
        if not species_columns:
            raise ValueError("wide CSV requires at least one species column")
        for line_number, row in enumerate(reader, start=2):
            site = (row[site_column] or "").strip()
            if not site:
                raise ValueError(f"line {line_number}: site is required")
            if site in communities:
                raise ValueError(f"line {line_number}: duplicate site '{site}'")
            abundances: dict[str, float] = {}
            for species in species_columns:
                try:
                    value = float(row[species])
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"line {line_number}: abundance for '{species}' must be numeric"
                    ) from exc
                if value < 0 or value != value or value == float("inf"):
                    raise ValueError(
                        f"line {line_number}: abundance for '{species}' "
                        "must be finite and non-negative"
                    )
                abundances[species] = value
            communities[site] = abundances
    if not communities:
        raise ValueError("CSV contains no observations")
    return communities


def read_communities_csv(
    path: str | Path, *, layout: str = "auto"
) -> dict[str, dict[str, float]]:
    """Read long or wide community data, optionally detecting the layout."""

    if layout not in {"auto", "long", "wide"}:
        raise ValueError("layout must be auto, long, or wide")
    if layout == "long":
        return read_long_csv(path)
    if layout == "wide":
        return read_wide_csv(path)
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        headers = set(next(csv.reader(handle), []))
    return (
        read_long_csv(path)
        if {"site", "species", "abundance"}.issubset(headers)
        else read_wide_csv(path)
    )


def read_traits_csv(
    path: str | Path, *, species_column: str = "species"
) -> dict[str, dict[str, float]]:
    """Read a numeric species-trait table."""

    traits: dict[str, dict[str, float]] = {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if species_column not in headers:
            raise ValueError(f"missing CSV column: {species_column}")
        trait_columns = [column for column in headers if column != species_column]
        if not trait_columns:
            raise ValueError("trait CSV requires at least one numeric trait")
        for line_number, row in enumerate(reader, start=2):
            species = (row[species_column] or "").strip()
            if not species:
                raise ValueError(f"line {line_number}: species is required")
            if species in traits:
                raise ValueError(f"line {line_number}: duplicate species '{species}'")
            try:
                traits[species] = {
                    trait: float(row[trait]) for trait in trait_columns
                }
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"line {line_number}: trait values must be numeric"
                ) from exc
    if not traits:
        raise ValueError("trait CSV contains no species")
    return traits
