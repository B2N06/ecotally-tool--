# Changelog

## 0.16.1 - 2026-07-01

- Add a complete Simplified Chinese guide.
- Add auditable formulas, assumptions, and interpretation boundaries.
- Add tests that keep package, citation, and documentation metadata aligned.

## 0.16.0 - 2026-07-01

- Add generalized Hill numbers for any finite non-negative order.
- Add `--hill-orders` for reproducible diversity profiles.
- Document how diversity order changes sensitivity to rare and dominant taxa.

## 0.15.0 - 2026-07-01

- Add reproducibility metadata to JSON and Markdown reports.
- Record software version, analysis settings, input filenames, and SHA-256.
- Hash trait files separately when functional analysis is requested.

## 0.14.0 - 2026-07-01

- Add deterministic z-score standardization for numeric trait tables.
- Map constant traits to zero so they cannot create false distances.
- Add `--standardize-traits` for safer mixed-unit functional analyses.

## 0.13.0 - 2026-07-01

- Add numeric species-trait table ingestion.
- Add community-weighted trait means, functional dispersion, and Rao's Q.
- Report abundance-weighted trait coverage to expose missing trait data.

## 0.12.0 - 2026-07-01

- Add square symmetric dissimilarity matrix output.
- Support Bray-Curtis, Jaccard, and Sørensen matrices.
- Produce plain CSV matrices for ordination, clustering, R, and GIS workflows.

## 0.11.0 - 2026-07-01

- Add Sørensen pairwise dissimilarity.
- Report species unique to each member of every site pair.
- Document incidence-based metric interpretation.

## 0.10.0 - 2026-07-01

- Expose individual-based rarefaction curves through `--rarefaction POINTS`.
- Add richness standardized to the smallest non-empty site total.
- Include tidy rarefaction rows in JSON and Markdown reports.

## 0.9.0 - 2026-07-01

- Add reproducible percentile bootstrap intervals for core diversity metrics.
- Add the `--bootstrap N` CLI option and report uncertainty as tidy rows.
- Preserve deterministic results with a documented fixed random seed.

## 0.8.0 - 2026-07-01

- Add structured ecological data-quality audits.
- Report empty sites without crashing an otherwise usable analysis.
- Flag all-zero species columns and severe sampling imbalance.
- Make CSV rendering robust to site rows with different available metrics.

## 0.7.0 - 2026-07-01

- Add dataset-scale gamma richness, mean alpha richness, and Whittaker beta.
- Add species occupancy and total-abundance summaries.
- Include dataset and species sections in JSON and Markdown reports.

## 0.6.0 - 2026-07-01

- Add self-contained Markdown biodiversity reports.
- Format numeric results consistently for human review.
- Document report generation for fieldwork and collaboration.

## 0.5.0 - 2026-07-01

- Add matrix-style wide CSV input.
- Detect long versus wide community tables automatically.
- Add explicit `--layout` override and a wide-table example.

## 0.4.0 - 2026-07-01

- Add Good sample coverage and bias-corrected Chao1 richness estimation.
- Add exact, individual-based rarefaction curves for count data.
- Include sampling-completeness estimates in CLI reports when applicable.

## 0.3.0 - 2026-07-01

- Add Jaccard and Bray-Curtis pairwise community comparisons.
- Return structured site and pairwise sections in JSON reports.
- Add contributor guidance and continuous integration.

## 0.2.0 - 2026-07-01

- Add long-form CSV ingestion and command-line CSV/JSON reports.
- Validate malformed and non-finite observations with useful errors.

## 0.1.0 - 2026-07-01

- Add alpha-diversity metrics and Hill numbers.
