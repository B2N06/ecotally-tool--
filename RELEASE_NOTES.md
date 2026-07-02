# EcoTally 0.27.3

EcoTally 0.27.3 makes longer analyses and result review easier to understand.
The analysis action now changes to a visible working state and ignores
duplicate clicks. Result export actions remain visible when tables expand,
and result rows are easier to scan.

## Desktop workflow

- Import CSV or TSV community data and preview it before analysis.
- Choose ecological questions using plain-language options.
- Review student-friendly conclusions alongside the underlying metrics.
- Export JSON reports or complete reproducible analysis bundles.
- Load a built-in example to learn the workflow safely.

## Included analyses

- Alpha diversity: richness, Shannon, Simpson, inverse Simpson, Pielou
  evenness, Berger-Parker dominance, and generalized Hill numbers.
- Sampling completeness: Good coverage, bias-corrected Chao1, exact
  individual-based rarefaction, and deterministic bootstrap intervals.
- Beta diversity: Jaccard, Sørensen, Bray-Curtis, turnover/nestedness
  partitioning, LCBD, SCBD, and LCBD permutation tests.
- Dataset summaries: alpha-beta-gamma partitioning, occupancy,
  rank-abundance data, standardized richness, and metadata-driven groups.
- Functional diversity: trait coverage, community-weighted means, functional
  dispersion, Rao's Q, and optional trait z-score standardization.
- Inference: deterministic two-group permutation tests for richness, Shannon,
  or Simpson means.

## Interoperability

- Long and wide community tables.
- Automatic comma, tab, and semicolon delimiter detection.
- Site metadata and numeric trait tables.
- CSV, JSON, Markdown, square distance matrices, accessible SVG, and
  self-describing multi-file bundles.
- SHA-256 provenance for every supplied source file.

## Validation

The release is validated on Python 3.10, 3.12, and 3.13 in GitHub Actions.
Local release checks include the full unit suite, bytecode compilation, wheel
construction, isolated wheel installation, CLI smoke tests, XML parsing of SVG
output, and analysis-bundle manifest inspection.

## Known boundaries

EcoTally does not infer detectability, causal effects, taxonomic correctness,
or sampling-design validity. Functional Euclidean distances require
appropriate trait scaling. Permutation tests assume exchangeable sampling
units. See [METHODOLOGY.md](METHODOLOGY.md) before interpreting results.
