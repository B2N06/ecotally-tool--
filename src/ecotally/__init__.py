"""Small, transparent tools for community ecology."""

__version__ = "0.6.0"

from .beta import PairwiseResult, compare_communities
from .diversity import DiversityResult, calculate_diversity
from .estimation import RichnessEstimate, estimate_richness, rarefaction_curve

__all__ = [
    "DiversityResult",
    "PairwiseResult",
    "calculate_diversity",
    "compare_communities",
    "RichnessEstimate",
    "estimate_richness",
    "rarefaction_curve",
]
