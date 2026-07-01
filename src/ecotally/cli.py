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
from .estimation import estimate_richness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecotally", description="Reproducible community-diversity summaries"
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("input", type=Path, help="long-form CSV input")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=("csv", "json", "markdown"),
        default="csv",
        help="output format",
    )
    parser.add_argument(
        "--layout",
        choices=("auto", "long", "wide"),
        default="auto",
        help="input layout (default: detect automatically)",
    )
    return parser


def analyze(
    path: Path, *, layout: str = "auto"
) -> dict[str, list[dict[str, object]]]:
    communities = read_communities_csv(path, layout=layout)
    sites: list[dict[str, object]] = []
    for site in sorted(communities):
        result = calculate_diversity(communities[site].values())
        row: dict[str, object] = {"site": site, **result.to_dict()}
        try:
            row.update(estimate_richness(communities[site].values()).to_dict())
        except ValueError:
            # Continuous measures (for example biomass) have valid diversity
            # metrics but no individual-based richness estimator.
            pass
        sites.append(row)
    pairwise: list[dict[str, object]] = []
    for first, second in combinations(sorted(communities), 2):
        result = compare_communities(communities[first], communities[second])
        pairwise.append(
            {"site_a": first, "site_b": second, **result.to_dict()}
        )
    return {"sites": sites, "pairwise": pairwise}


def render(report: dict[str, list[dict[str, object]]], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output_format == "markdown":
        return render_markdown(report)
    rows = report["sites"]
    if not rows:
        return ""
    from io import StringIO

    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
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
        "## Alpha diversity and sampling completeness\n\n"
        + _markdown_table(report["sites"])
        + "\n## Pairwise beta diversity\n\n"
        + _markdown_table(report["pairwise"])
        + "\n_Metrics are calculated by EcoTally. See the project documentation "
        "for formulas and data conventions._\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        content = render(analyze(args.input, layout=args.layout), args.format)
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
