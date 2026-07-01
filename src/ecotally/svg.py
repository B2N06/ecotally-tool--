"""Dependency-free SVG summaries."""

from __future__ import annotations

from html import escape


def render_diversity_svg(report: dict[str, list[dict[str, object]]]) -> str:
    """Render accessible horizontal bar charts for richness and Shannon."""

    sites = [
        row for row in report.get("sites", []) if "richness" in row and "shannon" in row
    ]
    if not sites:
        raise ValueError("SVG output requires at least one non-empty site")
    width = 900
    margin_left = 190
    chart_width = 620
    row_height = 34
    panel_height = 62 + len(sites) * row_height
    height = 54 + panel_height * 2
    colors = {"richness": "#287271", "shannon": "#D9822B"}
    labels = {"richness": "Species richness", "shannon": "Shannon diversity"}

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            'aria-labelledby="title desc">'
        ),
        "<title id=\"title\">EcoTally biodiversity summary</title>",
        (
            "<desc id=\"desc\">Horizontal bar charts comparing species richness "
            "and Shannon diversity among sites.</desc>"
        ),
        "<style>"
        "text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#18302B}"
        ".heading{font-size:22px;font-weight:700}"
        ".site{font-size:14px}.value{font-size:13px;font-weight:600}"
        ".grid{stroke:#DCE5E1;stroke-width:1}"
        "</style>",
        f'<rect width="{width}" height="{height}" fill="#F8FBF9"/>',
        '<text x="36" y="34" class="heading">EcoTally biodiversity summary</text>',
    ]
    y_offset = 54
    for metric in ("richness", "shannon"):
        maximum = max(float(row[metric]) for row in sites) or 1.0
        parts.append(
            f'<text x="36" y="{y_offset + 28}" class="heading">'
            f"{labels[metric]}</text>"
        )
        for index, row in enumerate(sites):
            y = y_offset + 48 + index * row_height
            site = escape(str(row["site"]))
            value = float(row[metric])
            bar_width = value / maximum * chart_width
            display = str(int(value)) if metric == "richness" else f"{value:.3f}"
            parts.extend(
                [
                    (
                        f'<text x="{margin_left - 12}" y="{y + 16}" '
                        f'text-anchor="end" class="site">{site}</text>'
                    ),
                    (
                        f'<line x1="{margin_left}" y1="{y + 22}" '
                        f'x2="{margin_left + chart_width}" y2="{y + 22}" '
                        'class="grid"/>'
                    ),
                    (
                        f'<rect x="{margin_left}" y="{y}" width="{bar_width:.2f}" '
                        f'height="22" rx="4" fill="{colors[metric]}"/>'
                    ),
                    (
                        f'<text x="{margin_left + bar_width + 8:.2f}" '
                        f'y="{y + 16}" class="value">{display}</text>'
                    ),
                ]
            )
        y_offset += panel_height
    parts.append("</svg>")
    return "\n".join(parts) + "\n"
