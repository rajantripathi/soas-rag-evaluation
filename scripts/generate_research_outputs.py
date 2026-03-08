#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "results" / "reports"
OUTPUT_DIR = REPORTS_DIR / "research_outputs"
SUMMARY_CSV = REPORTS_DIR / "project_synthesis_summary_20260309.csv"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_summary_rows() -> list[dict[str, str]]:
    with SUMMARY_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def make_bar_chart_svg(
    title: str,
    categories: list[str],
    series: list[tuple[str, list[float], str]],
    output_path: Path,
    y_max: float = 1.0,
) -> None:
    width = 900
    height = 520
    left = 90
    right = 40
    top = 70
    bottom = 110
    plot_width = width - left - right
    plot_height = height - top - bottom
    group_width = plot_width / max(len(categories), 1)
    bar_width = group_width / (len(series) + 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf5"/>',
        f'<text x="{width/2}" y="38" text-anchor="middle" font-family="Georgia, serif" font-size="24" fill="#1f2937">{title}</text>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#374151" stroke-width="2"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#374151" stroke-width="2"/>',
    ]

    for tick in range(6):
        value = y_max * tick / 5
        y = top + plot_height - (plot_height * value / y_max)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" stroke="#d1d5db" stroke-width="1"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#4b5563">{value:.1f}</text>')

    for group_idx, category in enumerate(categories):
        cx = left + group_idx * group_width
        parts.append(
            f'<text x="{cx + group_width/2:.1f}" y="{top + plot_height + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#111827">{category}</text>'
        )
        for series_idx, (_, values, color) in enumerate(series):
            value = values[group_idx]
            bar_h = plot_height * value / y_max
            x = cx + 10 + series_idx * bar_width
            y = top + plot_height - bar_h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 12:.1f}" height="{bar_h:.1f}" fill="{color}" rx="4"/>')
            parts.append(
                f'<text x="{x + (bar_width - 12)/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#111827">{value:.2f}</text>'
            )

    legend_x = left + plot_width - 180
    legend_y = 52
    for idx, (label, _, color) in enumerate(series):
        y = legend_y + idx * 22
        parts.append(f'<rect x="{legend_x}" y="{y - 11}" width="14" height="14" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{legend_x + 22}" y="{y}" font-family="Arial, sans-serif" font-size="13" fill="#111827">{label}</text>')

    parts.append("</svg>")
    write_text(output_path, "\n".join(parts))


def build_summary_tables(rows: list[dict[str, str]]) -> None:
    lookup = {row["condition"]: row for row in rows}

    baseline_rows = [
        {
            "condition": "baseline_vector",
            "overall_recall_at_k": lookup["vector_baseline"]["overall_recall_at_k"],
            "english_recall_at_k": lookup["vector_baseline"]["english_recall_at_k"],
            "uzbek_recall_at_k": lookup["vector_baseline"]["uzbek_recall_at_k"],
        },
        {
            "condition": "supplement_v1",
            "overall_recall_at_k": lookup["supplement_v1"]["overall_recall_at_k"],
            "english_recall_at_k": lookup["supplement_v1"]["english_recall_at_k"],
            "uzbek_recall_at_k": lookup["supplement_v1"]["uzbek_recall_at_k"],
        },
        {
            "condition": "supplement_v2",
            "overall_recall_at_k": lookup["supplement_v2"]["overall_recall_at_k"],
            "english_recall_at_k": lookup["supplement_v2"]["english_recall_at_k"],
            "uzbek_recall_at_k": lookup["supplement_v2"]["uzbek_recall_at_k"],
        },
    ]
    write_csv(
        OUTPUT_DIR / "table_baseline_vs_supplements.csv",
        baseline_rows,
        ["condition", "overall_recall_at_k", "english_recall_at_k", "uzbek_recall_at_k"],
    )

    language_rows = [
        {"language": "English", "recall_at_k": lookup["best_vector"]["english_recall_at_k"]},
        {"language": "Uzbek", "recall_at_k": lookup["best_vector"]["uzbek_recall_at_k"]},
    ]
    write_csv(OUTPUT_DIR / "table_language_comparison.csv", language_rows, ["language", "recall_at_k"])

    domain_rows = [
        {"language": "English", "governance": "0.8000", "history": "0.4000", "institutions": "0.3200", "culture": "1.0000"},
        {"language": "Uzbek", "governance": "0.9800", "history": "0.9600", "institutions": "0.9600", "culture": "0.9400"},
    ]
    write_csv(
        OUTPUT_DIR / "table_domain_comparison.csv",
        domain_rows,
        ["language", "governance", "history", "institutions", "culture"],
    )

    markdown = """# Summary Tables

## Baseline vs Supplement Gains
| Condition | Overall Recall@k | English Recall@k | Uzbek Recall@k |
| --- | ---: | ---: | ---: |
| baseline_vector | 0.5100 | 0.6300 | 0.3900 |
| supplement_v1 | 0.7150 | 0.6300 | 0.8000 |
| supplement_v2 | 0.8050 | 0.6300 | 0.9800 |

## Language Comparison Under Best Setup
| Language | Recall@k |
| --- | ---: |
| English | 0.6300 |
| Uzbek | 0.9600 |

## Domain Comparison Under Best Setup
| Language | Governance | History | Institutions | Culture |
| --- | ---: | ---: | ---: | ---: |
| English | 0.8000 | 0.4000 | 0.3200 | 1.0000 |
| Uzbek | 0.9800 | 0.9600 | 0.9600 | 0.9400 |
"""
    write_text(OUTPUT_DIR / "summary_tables.md", markdown)


def build_figures(rows: list[dict[str, str]]) -> None:
    lookup = {row["condition"]: row for row in rows}
    make_bar_chart_svg(
        title="Recall Improvement from Corpus Supplementation",
        categories=["Overall", "English", "Uzbek"],
        series=[
            ("Baseline", [0.51, 0.63, 0.39], "#c97b63"),
            ("Supplement v1", [0.715, 0.63, 0.80], "#4f772d"),
            ("Supplement v2", [0.805, 0.63, 0.98], "#1d4e89"),
        ],
        output_path=OUTPUT_DIR / "figure_baseline_vs_supplement.svg",
    )
    make_bar_chart_svg(
        title="Language Differences Under Best Setup",
        categories=["Governance", "History", "Institutions", "Culture"],
        series=[
            ("English", [0.80, 0.40, 0.32, 1.00], "#7c3aed"),
            ("Uzbek", [0.98, 0.96, 0.96, 0.94], "#0f766e"),
        ],
        output_path=OUTPUT_DIR / "figure_language_domain_comparison.svg",
    )


def main() -> int:
    ensure_dir(OUTPUT_DIR)
    rows = read_summary_rows()
    build_summary_tables(rows)
    build_figures(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
