"""Command-line interface for EcoTally."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from itertools import combinations
from pathlib import Path

from . import __version__
from .beta import compare_communities
from .diversity import calculate_diversity
from .io import read_communities_csv
from .estimation import estimate_richness, expected_richness, rarefaction_curve
from .summary import summarize_dataset, summarize_species
from .quality import audit_communities
from .uncertainty import bootstrap_diversity


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecotally", description="Reproducible community-diversity summaries"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("input", type=Path, help="long-form CSV input")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=("csv", "json", "markdown", "matrix"),
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
    return parser


def analyze(
    path: Path,
    *,
    layout: str = "auto",
    bootstrap: int = 0,
    rarefaction: int = 0,
) -> dict[str, list[dict[str, object]]]:
    communities = read_communities_csv(path, layout=layout)
    sites: list[dict[str, object]] = []
    uncertainty: list[dict[str, object]] = []
    rarefaction_rows: list[dict[str, object]] = []
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
    return {
        "dataset": [dataset],
        "sites": sites,
        "species": summarize_species(communities),
        "pairwise": pairwise,
        "quality": [issue.to_dict() for issue in audit_communities(communities)],
        "uncertainty": uncertainty,
        "rarefaction": rarefaction_rows,
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
        "## Dataset overview\n\n"
        + _markdown_table(report.get("dataset", []))
        + "\n"
        "## Alpha diversity and sampling completeness\n\n"
        + _markdown_table(report["sites"])
        + "\n## Species occupancy\n\n"
        + _markdown_table(report.get("species", []))
        + "\n## Pairwise beta diversity\n\n"
        + _markdown_table(report["pairwise"])
        + "\n## Data quality\n\n"
        + _markdown_table(report.get("quality", []))
        + "\n## Bootstrap uncertainty\n\n"
        + _markdown_table(report.get("uncertainty", []))
        + "\n## Rarefaction curves\n\n"
        + _markdown_table(report.get("rarefaction", []))
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
