# Changelog

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
