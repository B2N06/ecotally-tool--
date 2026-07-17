"""Small, transparent tools for community ecology."""

__version__ = "0.27.6"

from .beta import PairwiseResult, compare_communities
from .diversity import DiversityResult, calculate_diversity, hill_number
from .estimation import RichnessEstimate, estimate_richness, rarefaction_curve
from .summary import (
    DatasetSummary,
    rank_abundance,
    summarize_dataset,
    summarize_species,
)
from .quality import QualityIssue, audit_communities
from .uncertainty import bootstrap_diversity
from .functional import (
    FunctionalResult,
    calculate_functional_diversity,
    standardize_traits,
)
from .contribution import beta_contributions, lcbd_significance
from .inference import permutation_group_difference

__all__ = [
    "DiversityResult",
    "PairwiseResult",
    "calculate_diversity",
    "hill_number",
    "compare_communities",
    "RichnessEstimate",
    "estimate_richness",
    "rarefaction_curve",
    "DatasetSummary",
    "summarize_dataset",
    "summarize_species",
    "rank_abundance",
    "QualityIssue",
    "audit_communities",
    "bootstrap_diversity",
    "FunctionalResult",
    "calculate_functional_diversity",
    "standardize_traits",
    "beta_contributions",
    "lcbd_significance",
    "permutation_group_difference",
]
