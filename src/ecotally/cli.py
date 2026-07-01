"""Command-line interface for EcoTally."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

from . import __version__
from .beta import compare_communities
from .diversity import calculate_diversity, hill_number
from .io import read_communities_csv, read_site_metadata_csv, read_traits_csv
from .estimation import estimate_richness, expected_richness, rarefaction_curve
from .summary import rank_abundance, summarize_dataset, summarize_species
from .quality import audit_communities
from .uncertainty import bootstrap_diversity
from .functional import calculate_functional_diversity, standardize_traits
from .svg import render_diversity_svg
from .contribution import beta_contributions, lcbd_significance
from .inference import permutation_group_difference


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecotally", description="Reproducible community-diversity summaries"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("input", type=Path, help="long-form CSV input")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=("csv", "json", "markdown", "matrix", "svg", "bundle"),
        default="csv",
        help="output format",
    )
    parser.add_argument(
        "--layout",
        choices=("auto", "long", "wide"),
        default="auto",
        help="input layout (default: detect automatically)",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=0,
        metavar="N",
        help="add reproducible bootstrap intervals using N replicates",
    )
    parser.add_argument(
        "--rarefaction",
        type=int,
        default=0,
        metavar="POINTS",
        help="add individual-based rarefaction curves",
    )
    parser.add_argument(
        "--metric",
        choices=("jaccard", "sorensen", "bray_curtis"),
        default="bray_curtis",
        help="dissimilarity metric for matrix output",
    )
    parser.add_argument(
        "--traits",
        type=Path,
        help="numeric species-trait CSV for functional diversity",
    )
    parser.add_argument(
        "--standardize-traits",
        action="store_true",
        help="z-score traits before calculating functional distances",
    )
    parser.add_argument(
        "--hill-orders",
        type=_parse_hill_orders,
        default=[],
        metavar="Q,Q,...",
        help="add a Hill diversity profile for comma-separated orders",
    )
    parser.add_argument(
        "--lcbd-permutations",
        type=int,
        default=0,
        metavar="N",
        help="test LCBD significance using N column permutations",
    )
    parser.add_argument(
        "--site-metadata",
        type=Path,
        help="CSV with site-level grouping, location, or time fields",
    )
    parser.add_argument(
        "--group-by",
        help="site metadata field used for group-level community summaries",
    )
    parser.add_argument(
        "--group-permutations",
        type=int,
        default=0,
        metavar="N",
        help="test a two-group mean difference using N label permutations",
    )
    parser.add_argument(
        "--group-metric",
        choices=("richness", "shannon", "simpson"),
        default="shannon",
        help="site metric used by the two-group permutation test",
    )
    return parser


def _parse_hill_orders(value: str) -> list[float]:
    try:
        orders = [float(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Hill orders must be numbers") from exc
    if not orders or any(order < 0 for order in orders):
        raise argparse.ArgumentTypeError("Hill orders must be non-negative")
    return orders


def analyze(
    path: Path,
    *,
    layout: str = "auto",
    bootstrap: int = 0,
    rarefaction: int = 0,
    traits_path: Path | None = None,
    standardize_trait_values: bool = False,
    hill_orders: list[float] | None = None,
    lcbd_permutations: int = 0,
    site_metadata_path: Path | None = None,
    group_by: str | None = None,
    group_permutations: int = 0,
    group_metric: str = "shannon",
) -> dict[str, list[dict[str, object]]]:
    communities = read_communities_csv(path, layout=layout)
    site_metadata = (
        read_site_metadata_csv(site_metadata_path) if site_metadata_path else {}
    )
    traits = read_traits_csv(traits_path) if traits_path else None
    if traits and standardize_trait_values:
        traits = standardize_traits(traits)
    if group_by and not site_metadata_path:
        raise ValueError("--group-by requires --site-metadata")
    if group_permutations and not group_by:
        raise ValueError("--group-permutations requires --group-by")
    sites: list[dict[str, object]] = []
    uncertainty: list[dict[str, object]] = []
    rarefaction_rows: list[dict[str, object]] = []
    functional: list[dict[str, object]] = []
    hill_profile: list[dict[str, object]] = []
    for site in sorted(communities):
        row: dict[str, object] = {"site": site}
        if site in site_metadata:
            row.update(
                {
                    f"meta_{key}": value
                    for key, value in site_metadata[site].items()
                }
            )
        try:
            result = calculate_diversity(communities[site].values())
            row.update(result.to_dict())
            row.update(estimate_richness(communities[site].values()).to_dict())
        except ValueError:
            if sum(communities[site].values()) == 0:
                row["status"] = "empty"
            else:
                # Continuous measures (for example biomass) have valid
                # diversity metrics but no individual-based estimator.
                row.update(calculate_diversity(communities[site].values()).to_dict())
        sites.append(row)
        if bootstrap and sum(communities[site].values()) > 0:
            intervals = bootstrap_diversity(
                communities[site].values(), replicates=bootstrap
            )
            for metric, values in intervals.items():
                uncertainty.append({"site": site, "metric": metric, **values})
        if rarefaction and sum(communities[site].values()) > 0:
            for point in rarefaction_curve(
                communities[site].values(), points=rarefaction
            ):
                rarefaction_rows.append({"site": site, **point})
        if traits and sum(communities[site].values()) > 0:
            result = calculate_functional_diversity(communities[site], traits)
            functional.extend(result.to_rows(site))
        if hill_orders and sum(communities[site].values()) > 0:
            hill_profile.extend(
                {
                    "site": site,
                    "order": order,
                    "diversity": hill_number(communities[site].values(), order),
                }
                for order in hill_orders
            )
    pairwise: list[dict[str, object]] = []
    for first, second in combinations(sorted(communities), 2):
        try:
            result = compare_communities(communities[first], communities[second])
            pairwise.append(
                {"site_a": first, "site_b": second, **result.to_dict()}
            )
        except ValueError:
            pairwise.append(
                {"site_a": first, "site_b": second, "status": "undefined"}
            )
    dataset = summarize_dataset(communities).to_dict()
    positive_totals = [
        sum(community.values())
        for community in communities.values()
        if sum(community.values()) > 0
    ]
    if positive_totals and all(total.is_integer() for total in positive_totals):
        standardized_size = int(min(positive_totals))
        dataset["standardized_sample_size"] = standardized_size
        standardized = [
            expected_richness(community.values(), standardized_size)
            for community in communities.values()
            if sum(community.values()) > 0
        ]
        dataset["mean_standardized_richness"] = sum(standardized) / len(standardized)
    metadata: dict[str, object] = {
        "ecotally_version": __version__,
        "source_file": path.name,
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "input_layout": layout,
        "bootstrap_replicates": bootstrap,
        "rarefaction_points": rarefaction,
        "traits_standardized": standardize_trait_values,
        "hill_orders": ",".join(str(order) for order in (hill_orders or [])),
        "lcbd_permutations": lcbd_permutations,
        "group_by": group_by or "",
        "group_permutations": group_permutations,
        "group_metric": group_metric,
    }
    if traits_path:
        metadata["traits_file"] = traits_path.name
        metadata["traits_sha256"] = hashlib.sha256(
            traits_path.read_bytes()
        ).hexdigest()
    if site_metadata_path:
        metadata["site_metadata_file"] = site_metadata_path.name
        metadata["site_metadata_sha256"] = hashlib.sha256(
            site_metadata_path.read_bytes()
        ).hexdigest()
    metadata_issues: list[dict[str, str]] = []
    for site in sorted(set(communities) - set(site_metadata)):
        if site_metadata_path:
            metadata_issues.append(
                {
                    "severity": "warning",
                    "code": "missing_site_metadata",
                    "site": site,
                    "message": "Observation site has no matching metadata row.",
                }
            )
    for site in sorted(set(site_metadata) - set(communities)):
        metadata_issues.append(
            {
                "severity": "info",
                "code": "unused_site_metadata",
                "site": site,
                "message": "Metadata site has no observations.",
            }
        )
    group_summary: list[dict[str, object]] = []
    if group_by:
        known_fields = {
            field for values in site_metadata.values() for field in values
        }
        if group_by not in known_fields:
            raise ValueError(f"site metadata has no field '{group_by}'")
        groups: dict[str, dict[str, dict[str, float]]] = {}
        for site, community in communities.items():
            group = site_metadata.get(site, {}).get(group_by, "")
            if group:
                groups.setdefault(group, {})[site] = community
        if not groups:
            raise ValueError(f"site metadata field '{group_by}' has no usable values")
        for group, group_communities in sorted(groups.items()):
            result = summarize_dataset(group_communities).to_dict()
            group_summary.append(
                {"group_by": group_by, "group": group, **result}
            )
    group_test: list[dict[str, object]] = []
    if group_permutations and group_by:
        values_by_site = {
            str(row["site"]): float(row[group_metric])
            for row in sites
            if group_metric in row
        }
        groups_by_site = {
            site: values.get(group_by, "")
            for site, values in site_metadata.items()
        }
        group_test.append(
            permutation_group_difference(
                values_by_site,
                groups_by_site,
                metric=group_metric,
                permutations=group_permutations,
            )
        )
    contributions = beta_contributions(communities)
    return {
        "metadata": [metadata],
        "dataset": [dataset],
        "sites": sites,
        "species": summarize_species(communities),
        "rank_abundance": rank_abundance(communities),
        "pairwise": pairwise,
        "quality": [issue.to_dict() for issue in audit_communities(communities)],
        "uncertainty": uncertainty,
        "rarefaction": rarefaction_rows,
        "functional": functional,
        "hill_profile": hill_profile,
        "lcbd": contributions["lcbd"],
        "scbd": contributions["scbd"],
        "lcbd_significance": (
            lcbd_significance(communities, permutations=lcbd_permutations)
            if lcbd_permutations
            else []
        ),
        "metadata_issues": metadata_issues,
        "group_summary": group_summary,
        "group_test": group_test,
    }


def render(
    report: dict[str, list[dict[str, object]]],
    output_format: str,
    *,
    metric: str = "bray_curtis",
) -> str:
    if output_format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output_format == "markdown":
        return render_markdown(report)
    if output_format == "matrix":
        return render_matrix(report, metric)
    if output_format == "svg":
        return render_diversity_svg(report)
    rows = report["sites"]
    return _rows_to_csv(rows)


def _rows_to_csv(rows: list[dict[str, object]]) -> str:
    if not rows:
        return ""
    from io import StringIO

    buffer = StringIO(newline="")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def write_bundle(
    report: dict[str, list[dict[str, object]]], output_dir: Path
) -> list[str]:
    """Write a deterministic multi-file analysis bundle."""

    output_dir.mkdir(parents=True, exist_ok=True)
    written = ["report.json"]
    (output_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for section, rows in report.items():
        if rows:
            filename = f"{section}.csv"
            (output_dir / filename).write_text(
                _rows_to_csv(rows), encoding="utf-8"
            )
            written.append(filename)
    manifest = {
        "format": "ecotally-analysis-bundle",
        "version": 1,
        "ecotally_version": __version__,
        "files": written,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["manifest.json", *written]


def render_matrix(
    report: dict[str, list[dict[str, object]]], metric: str
) -> str:
    """Render a square, symmetric dissimilarity matrix as CSV."""

    field = f"{metric}_dissimilarity"
    sites = sorted(str(row["site"]) for row in report["sites"])
    values = {(site, site): 0.0 for site in sites}
    for row in report["pairwise"]:
        if field in row:
            first, second = str(row["site_a"]), str(row["site_b"])
            values[(first, second)] = values[(second, first)] = float(row[field])

    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["site", *sites])
    for site in sites:
        writer.writerow(
            [site, *(values.get((site, other), "") for other in sites)]
        )
    return buffer.getvalue()


def _display(value: object) -> str:
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def _markdown_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "_No comparisons available._\n"
    columns = list(rows[0])
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines.extend(
        "| " + " | ".join(_display(row.get(column, "")) for column in columns) + " |"
        for row in rows
    )
    return "\n".join(lines) + "\n"


def render_markdown(report: dict[str, list[dict[str, object]]]) -> str:
    """Render a self-contained, human-readable analysis report."""

    return (
        "# EcoTally biodiversity report\n\n"
        "## Reproducibility metadata\n\n"
        + _markdown_table(report.get("metadata", []))
        + "\n"
        "## Dataset overview\n\n"
        + _markdown_table(report.get("dataset", []))
        + "\n"
        "## Alpha diversity and sampling completeness\n\n"
        + _markdown_table(report["sites"])
        + "\n## Species occupancy\n\n"
        + _markdown_table(report.get("species", []))
        + "\n## Rank-abundance data\n\n"
        + _markdown_table(report.get("rank_abundance", []))
        + "\n## Pairwise beta diversity\n\n"
        + _markdown_table(report["pairwise"])
        + "\n## Data quality\n\n"
        + _markdown_table(report.get("quality", []))
        + "\n## Bootstrap uncertainty\n\n"
        + _markdown_table(report.get("uncertainty", []))
        + "\n## Rarefaction curves\n\n"
        + _markdown_table(report.get("rarefaction", []))
        + "\n## Functional diversity\n\n"
        + _markdown_table(report.get("functional", []))
        + "\n## Hill diversity profile\n\n"
        + _markdown_table(report.get("hill_profile", []))
        + "\n## Local contributions to beta diversity\n\n"
        + _markdown_table(report.get("lcbd", []))
        + "\n## Species contributions to beta diversity\n\n"
        + _markdown_table(report.get("scbd", []))
        + "\n## LCBD permutation significance\n\n"
        + _markdown_table(report.get("lcbd_significance", []))
        + "\n## Site metadata issues\n\n"
        + _markdown_table(report.get("metadata_issues", []))
        + "\n## Group summaries\n\n"
        + _markdown_table(report.get("group_summary", []))
        + "\n## Two-group permutation test\n\n"
        + _markdown_table(report.get("group_test", []))
        + "\n_Metrics are calculated by EcoTally. See the project documentation "
        "for formulas and data conventions._\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze(
            args.input,
            layout=args.layout,
            bootstrap=args.bootstrap,
            rarefaction=args.rarefaction,
            traits_path=args.traits,
            standardize_trait_values=args.standardize_traits,
                hill_orders=args.hill_orders,
                lcbd_permutations=args.lcbd_permutations,
                site_metadata_path=args.site_metadata,
                group_by=args.group_by,
                group_permutations=args.group_permutations,
                group_metric=args.group_metric,
        )
        if args.format == "bundle":
            if not args.output:
                raise ValueError("bundle format requires --output DIRECTORY")
            write_bundle(report, args.output)
            return 0
        content = render(report, args.format, metric=args.metric)
        if args.output:
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
        return 0
    except (OSError, ValueError) as exc:
        print(f"ecotally: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
