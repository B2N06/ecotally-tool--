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
from .io import read_communities_csv, read_traits_csv
from .estimation import estimate_richness, expected_richness, rarefaction_curve
from .summary import rank_abundance, summarize_dataset, summarize_species
from .quality import audit_communities
from .uncertainty import bootstrap_diversity
from .functional import calculate_functional_diversity, standardize_traits
from .svg import render_diversity_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecotally", description="Reproducible community-diversity summaries"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("input", type=Path, help="long-form CSV input")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=("csv", "json", "markdown", "matrix", "svg"),
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
) -> dict[str, list[dict[str, object]]]:
    communities = read_communities_csv(path, layout=layout)
    traits = read_traits_csv(traits_path) if traits_path else None
    if traits and standardize_trait_values:
        traits = standardize_traits(traits)
    sites: list[dict[str, object]] = []
    uncertainty: list[dict[str, object]] = []
    rarefaction_rows: list[dict[str, object]] = []
    functional: list[dict[str, object]] = []
    hill_profile: list[dict[str, object]] = []
    for site in sorted(communities):
        row: dict[str, object] = {"site": site}
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
    }
    if traits_path:
        metadata["traits_file"] = traits_path.name
        metadata["traits_sha256"] = hashlib.sha256(
            traits_path.read_bytes()
        ).hexdigest()
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
    if not rows:
        return ""
    from io import StringIO

    buffer = StringIO(newline="")
    columns = list(dict.fromkeys(key for row in rows for key in row))
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


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
        + "\n_Metrics are calculated by EcoTally. See the project documentation "
        "for formulas and data conventions._\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        content = render(
            analyze(
                args.input,
                layout=args.layout,
                bootstrap=args.bootstrap,
                rarefaction=args.rarefaction,
                traits_path=args.traits,
                standardize_trait_values=args.standardize_traits,
                hill_orders=args.hill_orders,
            ),
            args.format,
            metric=args.metric,
        )
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
