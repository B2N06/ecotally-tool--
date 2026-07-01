# EcoTally

[简体中文](README.zh-CN.md) · [Methods and formulas](METHODOLOGY.md) ·
[Contributing](CONTRIBUTING.md) · [Release notes](RELEASE_NOTES.md) ·
[Roadmap](ROADMAP.md)

EcoTally is a small, auditable open-source toolkit for community ecology.
It turns species-abundance observations into reproducible biodiversity
summaries without hiding calculations behind a large software stack.

EcoTally provides Shannon diversity, Simpson diversity, inverse Simpson,
Pielou evenness, Hill numbers (q = 0, 1, 2), Jaccard and Sørensen
dissimilarity, and Bray-Curtis dissimilarity. Pairwise results also identify
shared and site-unique species. Integer count data receives sample coverage,
bias-corrected Chao1 richness, and individual-based rarefaction support.
Dataset reports partition alpha, beta, and gamma richness and summarize species
occupancy across sites.
Built-in quality checks flag empty sites, all-zero species, single-site inputs,
and severe sampling imbalance before results are interpreted.
Reports also include Berger-Parker dominance and tidy rank-abundance data for
inspecting dominant and rare species.
Hellinger-based LCBD and SCBD partitions identify unusually composed sites and
the species contributing most to overall beta diversity.
Pairwise Sørensen dissimilarity is partitioned into turnover and nestedness,
distinguishing species replacement from richness differences.

Test LCBD against independently permuted species columns:

```shell
python -m ecotally examples/observations.csv --lcbd-permutations 999 \
  --format markdown
```

Permutation tests use a fixed seed by default and report the corrected
`(exceedances + 1) / (permutations + 1)` p-value.

```python
from ecotally import calculate_diversity

result = calculate_diversity([12, 7, 3, 1])
print(result.to_dict())
```

Analyze a long-form CSV with the columns `site,species,abundance`:

```shell
python -m ecotally examples/observations.csv
python -m ecotally examples/observations.csv --format json -o report.json
python -m ecotally examples/observations.csv --format markdown -o report.md
```

Matrix-style CSV files are detected automatically:

```shell
python -m ecotally examples/community-matrix.csv
```

Repeated observations of a species at the same site are summed. UTF-8 files
with or without a BOM are accepted. JSON reports contain both per-site
diversity and every pairwise site comparison. CSV output contains per-site
metrics for convenient spreadsheet use.
Markdown reports are ready to attach to fieldwork notes or repository issues.
Input delimiters are detected automatically for comma-separated, tab-separated,
and semicolon-separated community, trait, and site metadata tables.

Add deterministic percentile bootstrap intervals for integer count data:

```shell
python -m ecotally examples/observations.csv --format markdown --bootstrap 999
```

The default random seed is fixed, so identical inputs and settings produce
identical intervals.

Generate rarefaction curves with a chosen number of points:

```shell
python -m ecotally examples/observations.csv --format json --rarefaction 20
```

For integer count datasets, EcoTally also reports mean richness standardized
to the smallest non-empty site total.

Export a square distance matrix for clustering, ordination, R, or GIS:

```shell
python -m ecotally examples/observations.csv --format matrix
python -m ecotally examples/observations.csv --format matrix --metric jaccard
```

Analyze numeric functional traits:

```shell
python -m ecotally examples/observations.csv --traits examples/traits.csv \
  --standardize-traits --format markdown -o functional-report.md
```

Functional reports include trait coverage, abundance-weighted trait means,
functional dispersion, and Rao's quadratic entropy. Trait distances are
Euclidean; standardize columns first when units or scales differ strongly.
The `--standardize-traits` option performs a population z-score across species;
constant traits become zero and therefore do not affect distances.

## Reproducibility

JSON and Markdown reports record the EcoTally version, analysis options,
source filenames, and SHA-256 hashes of observation and trait files. The hash
lets collaborators verify that two reports used byte-identical input without
embedding private field data in the report.

Generate a Hill diversity profile to inspect sensitivity to rare versus
dominant species:

```shell
python -m ecotally examples/observations.csv --format markdown \
  --hill-orders 0,0.5,1,2,3
```

Order 0 is richness, order 1 is the exponential of Shannon entropy, and order
2 is inverse Simpson. Higher orders increasingly emphasize dominant species.

Create an accessible, publication-friendly vector summary with no plotting
dependencies:

```shell
python -m ecotally examples/observations.csv --format svg -o diversity.svg
```

Export a self-describing analysis bundle with full JSON, a manifest, and one
CSV per non-empty report section:

```shell
python -m ecotally examples/observations.csv --format bundle -o analysis
```

Join arbitrary site-level fields such as treatment, habitat, year, or
coordinates:

```shell
python -m ecotally examples/observations.csv \
  --site-metadata examples/site-metadata.csv --format json
```

Joined fields use a `meta_` prefix. Reports flag observation sites without
metadata and metadata rows without observations.

Summarize communities by a metadata field:

```shell
python -m ecotally examples/observations.csv \
  --site-metadata examples/site-metadata.csv --group-by habitat \
  --format markdown
```

Each group receives site count, gamma richness, mean alpha richness, Whittaker
beta, and total abundance.

For exactly two groups, test the mean difference in a site-level metric:

```shell
python -m ecotally examples/observations.csv \
  --site-metadata examples/site-metadata.csv --group-by habitat \
  --group-metric shannon --group-permutations 999 --format markdown
```

The report defines the effect as `mean(group_b) - mean(group_a)`, with group
names sorted for deterministic direction, and reports a corrected two-sided
permutation p-value.

## Development

```shell
python -m pip install -e .
python -m unittest discover -s tests
```

## Data conventions

- Each row is an observation; duplicate site/species rows are summed.
- Wide tables use `site` as the first column and species names as other columns.
- Abundance may be an integer count or a non-negative continuous quantity.
- Zero-abundance records do not contribute to richness or incidence.
- Shannon uses natural logarithms. Simpson is reported as `1 - sum(p²)`.
- Jaccard uses presence/absence; Bray-Curtis uses abundance.
- Sørensen uses presence/absence and gives shared species twice the weight.

EcoTally is released under the MIT License.
