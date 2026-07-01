"""Small, transparent tools for community ecology."""

__version__ = "0.15.0"

from .beta import PairwiseResult, compare_communities
from .diversity import DiversityResult, calculate_diversity
from .estimation import RichnessEstimate, estimate_richness, rarefaction_curve
from .summary import DatasetSummary, summarize_dataset, summarize_species
from .quality import QualityIssue, audit_communities
from .uncertainty import bootstrap_diversity
from .functional import (
    FunctionalResult,
    calculate_functional_diversity,
    standardize_traits,
)

__all__ = [
    "DiversityResult",
    "PairwiseResult",
    "calculate_diversity",
    "compare_communities",
    "RichnessEstimate",
    "estimate_richness",
    "rarefaction_curve",
    "DatasetSummary",
    "summarize_dataset",
    "summarize_species",
    "QualityIssue",
    "audit_communities",
    "bootstrap_diversity",
    "FunctionalResult",
    "calculate_functional_diversity",
    "standardize_traits",
]
