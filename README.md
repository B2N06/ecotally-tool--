# EcoTally

EcoTally is a small, auditable open-source toolkit for community ecology.
It turns species-abundance observations into reproducible biodiversity
summaries without hiding calculations behind a large software stack.

EcoTally provides Shannon diversity, Simpson diversity, inverse Simpson,
Pielou evenness, Hill numbers (q = 0, 1, 2), Jaccard dissimilarity, and
Bray-Curtis dissimilarity. Integer count data also receives sample coverage,
bias-corrected Chao1 richness, and individual-based rarefaction support.

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

EcoTally is released under the MIT License.
