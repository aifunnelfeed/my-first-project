#!/usr/bin/env python3
"""Build HTML X-ray report from project's xray.md."""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

# --- Config ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"
XRAYS_DIR = PROJECT_ROOT / "xrays"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DOCS_DIR = PROJECT_ROOT / "docs"

MD = markdown.Markdown(extensions=["extra"])


def _md(text: str) -> str:
    """Convert markdown to HTML and reset parser."""
    html = MD.convert(text.strip())
    MD.reset()
    return html


# --- Data classes ---


@dataclass
class SummaryRow:
    label: str
    value: str


@dataclass
class StructureRow:
    num: str
    component: str
    status: str
    status_class: str = ""  # "found", "weak", "missing"


@dataclass
class ScoreRow:
    num: str
    dimension: str
    score: str
    score_num: int = 0
    status: str = ""  # emoji
    status_class: str = ""  # "green", "yellow", "red"
    comment: str = ""


@dataclass
class CalcRow:
    num: str
    dimension: str
    score: str
    weight: str
    weighted: str


@dataclass
class Recommendation:
    num: int
    priority: str  # "red" or "yellow"
    title: str
    body_html: str


@dataclass
class DetailSection:
    name: str
    html: str


@dataclass
class XrayReport:
    title: str = ""
    overall_score: int = 0
    score_class: str = ""  # "green", "yellow", "red"
    summary: list = field(default_factory=list)
    structure: list = field(default_factory=list)
    scores: list = field(default_factory=list)
    details: list = field(default_factory=list)
    calculation: list = field(default_factory=list)
    calc_total_line: str = ""
    recommendations: list = field(default_factory=list)
    kb_comparison_html: str = ""
    verdict_html: str = ""


# --- Parsing ---

RE_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
RE_TABLE_SEP = re.compile(r"^[\|\s\-:]+$")


def _parse_table(text: str, skip_header: bool = True) -> list[list[str]]:
    """Parse a markdown table into rows of cells.

    If skip_header is True, the first data row (before the separator line)
    is treated as a header and excluded from the result.
    """
    rows = []
    found_sep = False
    header_row = None
    for line in text.strip().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if RE_TABLE_SEP.match(line):
            found_sep = True
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if skip_header and not found_sep:
            header_row = cells  # noqa: F841
            continue
        rows.append(cells)
    return rows


def _score_class(score: int) -> str:
    if score >= 80:
        return "green"
    elif score >= 50:
        return "yellow"
    return "red"


def _status_class_from_text(status: str) -> str:
    s = status.upper()
    if "НАЙДЕН" in s and "НЕ " not in s:
        if "СЛАБ" in s:
            return "weak"
        return "found"
    if "НЕ НАЙДЕН" in s or "НЕТ" in s:
        return "missing"
    if "СЛАБ" in s:
        return "weak"
    return "found"


def _emoji_to_class(text: str) -> str:
    if "🔴" in text:
        return "red"
    if "🟡" in text:
        return "yellow"
    if "🟢" in text:
        return "green"
    return ""


def parse_xray_md(text: str) -> XrayReport:
    """Parse xray.md into structured report data."""
    report = XrayReport()

    # --- Title ---
    m = re.search(r"^#\s+РЕНТГЕН:\s*(.+)$", text, re.MULTILINE)
    if m:
        report.title = m.group(1).strip()

    # --- Split by ## sections ---
    sections = re.split(r"^##\s+", text, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Get section heading (first line)
        first_line, _, body = section.partition("\n")
        heading = first_line.strip()
        body = body.strip()

        if heading.startswith("Сводка"):
            _parse_summary(body, report)
        elif heading.startswith("Структура"):
            _parse_structure(body, report)
        elif heading.startswith("Оценка по измерениям") and "расчёт" not in heading.lower():
            _parse_scores(body, report)
        elif "расчёт" in heading.lower():
            _parse_calculation(body, report)
        elif heading.startswith("Детальный"):
            _parse_details(body, report)
        elif heading.startswith("Рекомендации"):
            _parse_recommendations(body, report)
        elif heading.startswith("Сравнение"):
            report.kb_comparison_html = _md(body)
        elif heading.startswith("Итоговый"):
            report.verdict_html = _md(body)

    return report


def _parse_summary(body: str, report: XrayReport):
    rows = _parse_table(body)
    for row in rows:
        if len(row) >= 2:
            label = row[0].strip()
            value = row[1].strip()
            report.summary.append(SummaryRow(label=label, value=value))
            # Extract overall score
            if "балл" in label.lower():
                m = re.search(r"(\d+)", value)
                if m:
                    report.overall_score = int(m.group(1))
                    report.score_class = _score_class(report.overall_score)


def _parse_structure(body: str, report: XrayReport):
    rows = _parse_table(body)
    for row in rows:
        if len(row) >= 3:
            report.structure.append(StructureRow(
                num=row[0].strip(),
                component=re.sub(r"\*\*(.+?)\*\*", r"\1", row[1].strip()),
                status=row[2].strip(),
                status_class=_status_class_from_text(row[2]),
            ))


def _parse_scores(body: str, report: XrayReport):
    rows = _parse_table(body)
    for row in rows:
        if len(row) >= 5:
            score_text = row[2].strip()
            m = re.search(r"(\d+)", score_text)
            score_num = int(m.group(1)) if m else 0
            status = row[3].strip()
            report.scores.append(ScoreRow(
                num=row[0].strip(),
                dimension=row[1].strip(),
                score=score_text,
                score_num=score_num,
                status=status,
                status_class=_emoji_to_class(status),
                comment=row[4].strip(),
            ))


def _parse_details(body: str, report: XrayReport):
    # Split by ### headings
    parts = re.split(r"^###\s+", body, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        first_line, _, rest = part.partition("\n")
        name = first_line.strip()
        html = _md(rest.strip()) if rest.strip() else ""
        report.details.append(DetailSection(name=name, html=html))


def _parse_calculation(body: str, report: XrayReport):
    rows = _parse_table(body)
    for row in rows:
        if len(row) >= 5:
            # Check if it's the total row
            if "итого" in row[1].lower() or "итого" in row[0].lower():
                report.calc_total_line = " | ".join(c.strip() for c in row)
            else:
                report.calculation.append(CalcRow(
                    num=row[0].strip(),
                    dimension=row[1].strip(),
                    score=row[2].strip(),
                    weight=row[3].strip(),
                    weighted=row[4].strip(),
                ))

    # Also get the formula line after the table
    lines = body.strip().splitlines()
    for line in lines:
        if "Общий балл" in line and "=" in line:
            report.calc_total_line = line.strip()
            break


def _parse_recommendations(body: str, report: XrayReport):
    # Split by numbered items: 1. **🔴 ... or 1. **🟡 ...
    items = re.split(r"^\d+\.\s+", body, flags=re.MULTILINE)
    num = 0
    for item in items:
        item = item.strip()
        if not item:
            continue
        num += 1

        # Extract priority emoji
        priority = "yellow"
        if "🔴" in item:
            priority = "red"

        # Extract title: **🔴/🟡 Title**
        m = re.match(r"\*\*[🔴🟡🟢]\s*(.+?)\*\*", item)
        title = m.group(1).strip() if m else item.split("\n")[0]

        # Rest is body
        first_line_end = item.find("\n")
        rec_body = item[first_line_end:].strip() if first_line_end > 0 else ""

        report.recommendations.append(Recommendation(
            num=num,
            priority=priority,
            title=title,
            body_html=_md(rec_body) if rec_body else "",
        ))


# --- Build ---


def build(project: str, input_file: str, source: str = "projects"):
    """Build HTML X-ray report from project or external xrays markdown."""
    if source == "xrays":
        md_path = XRAYS_DIR / project / input_file
    else:
        md_path = PROJECTS_DIR / project / input_file
    if not md_path.exists():
        print(f"ERROR: {md_path} not found")
        return

    text = md_path.read_text(encoding="utf-8")

    # Parse
    report = parse_xray_md(text)

    if not report.title:
        report.title = f"X-ray: {project}"

    # Load template
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("xray.html")

    html = template.render(report=report, project=project)

    # Write output
    out_dir = DOCS_DIR / project
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "xray.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"OK: {out_path.relative_to(PROJECT_ROOT)}")
    print(f"    Score: {report.overall_score}/100 ({report.score_class})")
    print(f"    Sections: summary={len(report.summary)}, structure={len(report.structure)}, "
          f"scores={len(report.scores)}, details={len(report.details)}, "
          f"recommendations={len(report.recommendations)}")


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="Build HTML X-ray report from xray.md"
    )
    parser.add_argument("project", help="Project slug (folder name in projects/ or xrays/)")
    parser.add_argument(
        "--input", default="xray.md", help="Markdown file name (default: xray.md)"
    )
    parser.add_argument(
        "--source", default="projects", choices=["projects", "xrays"],
        help="Source directory: 'projects' (default) or 'xrays' for external site reports"
    )
    args = parser.parse_args()

    build(args.project, args.input, args.source)


if __name__ == "__main__":
    main()
