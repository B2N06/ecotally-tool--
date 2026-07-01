# Methods and formulas

EcoTally favors explicit, auditable definitions. Let `nᵢ` be the abundance of
species `i`, `N = Σnᵢ`, and `pᵢ = nᵢ/N`. Species with zero abundance are
excluded from diversity calculations.

## Alpha diversity

- Richness: `S = number of species with nᵢ > 0`.
- Shannon entropy: `H′ = -Σ pᵢ ln(pᵢ)`.
- Simpson diversity: `1 - Σpᵢ²`.
- Inverse Simpson: `1 / Σpᵢ²`.
- Pielou evenness: `J′ = H′ / ln(S)`; defined as 1 for one-species samples.
- Berger-Parker dominance: `max(pᵢ)`.
- Hill number: `Dq = (Σpᵢ^q)^(1/(1-q))`; its limit at `q=1` is `exp(H′)`.

## Sampling completeness

For integer counts, Good sample coverage is `1 - f₁/N`, where `f₁` is the
number of singleton species. Bias-corrected Chao1 is
`S + f₁(f₁-1) / (2(f₂+1))`, where `f₂` is the number of doubletons.

Expected richness in an individual-based rarefied sample of size `m` is:

`Σ[1 - C(N-nᵢ,m) / C(N,m)]`.

Bootstrap intervals resample `N` observed individuals with replacement and
use equal-tailed percentile bounds. The CLI uses a fixed seed for reproducible
reports; these intervals describe resampling uncertainty, not every source of
ecological or sampling uncertainty.

## Beta and gamma diversity

- Jaccard dissimilarity: `1 - c/(a+b-c)`.
- Sørensen dissimilarity: `1 - 2c/(a+b)`.
- Bray–Curtis dissimilarity: `Σ|xᵢ-yᵢ| / Σ(xᵢ+yᵢ)`.
- Whittaker beta: gamma richness divided by mean alpha richness.

Here `a` and `b` are site richnesses and `c` is shared richness. Gamma
richness is the union of observed species across sites.

LCBD and SCBD are calculated by Hellinger-transforming each non-empty site's
relative abundances (`sqrt(pᵢ)`), centering every species column, and
partitioning the total squared deviation among site rows (LCBD) and species
columns (SCBD). Each set sums to one when there is compositional variation.

## Functional diversity

Community-weighted means use abundance renormalized over species with trait
data. Trait coverage is the proportion of total abundance represented by
those species. Functional dispersion is the weighted mean Euclidean distance
to the abundance-weighted trait centroid. Rao's Q is:

`ΣᵢΣⱼ pᵢpⱼdᵢⱼ`.

Because Euclidean distance is scale-sensitive, `--standardize-traits`
population-z-scores each trait across supplied species. Constant traits map to
zero. Missing-trait species are excluded from functional calculations and
their loss is exposed by trait coverage.

## Important boundaries

EcoTally does not infer detectability, sampling design, taxonomy, causality, or
statistical independence. Compare sites only when field methods and effort are
commensurable, or use rarefaction and clearly document remaining limitations.
