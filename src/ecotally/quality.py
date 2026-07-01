"""Data-quality checks for ecological community tables."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True)
class QualityIssue:
    """A reproducible warning about an input dataset."""

    severity: str
    code: str
    message: str
    subject: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def audit_communities(
    communities: Mapping[str, Mapping[str, float]],
) -> list[QualityIssue]:
    """Identify common problems that can distort biodiversity comparisons."""

    issues: list[QualityIssue] = []
    totals: dict[str, float] = {}
    all_species = {
        species for community in communities.values() for species in community
    }
    for site, community in sorted(communities.items()):
        total = sum(float(value) for value in community.values())
        totals[site] = total
        if total == 0:
            issues.append(
                QualityIssue(
                    "error",
                    "empty_site",
                    "Site has zero total abundance; diversity is undefined.",
                    site,
                )
            )
    for species in sorted(all_species):
        if all(float(community.get(species, 0)) == 0 for community in communities.values()):
            issues.append(
                QualityIssue(
                    "warning",
                    "unobserved_species",
                    "Species column contains only zeros.",
                    species,
                )
            )
    positive_totals = [total for total in totals.values() if total > 0]
    if len(positive_totals) > 1 and max(positive_totals) / min(positive_totals) >= 10:
        issues.append(
            QualityIssue(
                "warning",
                "sampling_imbalance",
                "Largest site total is at least 10× the smallest; compare "
                "richness using rarefaction or standardized effort.",
            )
        )
    if len(communities) == 1:
        issues.append(
            QualityIssue(
                "info",
                "single_site",
                "Only one site is present; beta diversity cannot be estimated.",
            )
        )
    return issues
