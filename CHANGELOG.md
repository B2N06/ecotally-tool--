# Changelog

## 0.27.6 - 2026-07-17

- Exclude unused socket, TLS, HTTP, and browser-launch modules from the
  packaged desktop executable while retaining the standard-library parsing
  code required by PyInstaller.
- Add a packaged analysis self-test to catch executable-only startup failures.
- Add Windows product/version metadata and reproducible SHA-256 sidecars.
- Add optional Authenticode and Microsoft Artifact Signing release paths.
- Add GitHub build provenance attestations for Windows artifacts.
- Document the difference between Firewall and SmartScreen warnings.

## 0.27.5 - 2026-07-02

- Add a compact student guide for richness, Shannon, Simpson, and evenness.
- State the Simpson convention used by EcoTally directly on the results page.
- Reuse the same metric guidance in the built-in help page.

## 0.27.4 - 2026-07-02

- Report equal richness across all sites instead of selecting an arbitrary
  “highest” site.
- Report tied leaders for richness and evenness explicitly.
- Add regression coverage for equal and tied site summaries.

## 0.27.3 - 2026-07-02

- Show a clear in-progress state while an analysis is running.
- Ignore duplicate clicks on the analysis action.
- Keep result export actions visible when the results table expands.
- Add bordered, alternating rows to the site-results table.

## 0.27.2 - 2026-07-02

- Keep the primary import action visible when the app is resized to its
  minimum supported height.
- Reserve the bottom action bar before allowing the data preview to expand.

## 0.27.1 - 2026-07-02

- Increase contrast between the application background and white content surfaces.
- Give the selected-data card a green tint, stronger border, and bold filename.
- Add a visible preview-table boundary and alternating row backgrounds.

## 0.27.0 - 2026-07-02

- Add a native three-step Windows desktop interface for biology students.
- Add file preview, student-facing analysis choices, result summaries, and exports.
- Add a reproducible PyInstaller build script for a single-file GUI executable.

## 0.26.0 - 2026-07-01

- Detect comma, tab, and semicolon delimiters automatically.
- Apply delimiter detection consistently to communities, traits, and metadata.
- Add TSV and semicolon-separated input regression coverage.

## 0.25.0 - 2026-07-01

- Add reproducible two-group permutation tests for site metrics.
- Compare richness, Shannon, or Simpson means with deterministic effect direction.
- Record metric and permutation settings in report provenance.

## 0.24.0 - 2026-07-01

- Add metadata-driven group summaries with `--group-by`.
- Report group site count, gamma richness, mean alpha, Whittaker beta, and abundance.
- Validate missing metadata files, unknown fields, and empty group values.

## 0.23.0 - 2026-07-01

- Add site-level metadata ingestion and safe `meta_` field joins.
- Hash metadata files in reproducibility provenance.
- Flag missing observation metadata and unused metadata rows.

## 0.22.0 - 2026-07-01

- Partition Sørensen dissimilarity into turnover and nestedness.
- Distinguish species replacement from richness-driven subset patterns.
- Add decomposition identity and pure-nestedness regression tests.

## 0.21.0 - 2026-07-01

- Add reproducible column-permutation significance tests for LCBD.
- Report finite-randomization corrected p-values and permutation counts.
- Store LCBD permutation settings in report provenance.

## 0.20.0 - 2026-07-01

- Add Hellinger-based local contributions to beta diversity (LCBD).
- Add species contributions to beta diversity (SCBD).
- Expose which sites and taxa drive whole-dataset compositional variation.

## 0.19.0 - 2026-07-01

- Add self-describing multi-file analysis bundles.
- Export full JSON plus one CSV for every non-empty report section.
- Add a deterministic manifest with format and EcoTally versions.

## 0.18.0 - 2026-07-01

- Add Berger-Parker dominance to every non-empty site summary.
- Add deterministic rank-abundance rows with species and relative abundance.
- Expose data needed for dominance inspection and rank-abundance curves.

## 0.17.0 - 2026-07-01

- Add dependency-free SVG richness and Shannon charts.
- Include accessible titles, descriptions, site labels, and exact values.
- Add vector output suitable for documents, repository pages, and presentations.

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
