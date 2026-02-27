#!/usr/bin/env python3
"""Build HTML landing page from project's final.md."""

import argparse
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

# --- Config ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = PROJECT_ROOT / "projects"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
DOCS_DIR = PROJECT_ROOT / "docs"

MAX_HERO_PARAGRAPHS = 5

# --- Section types ---


class SectionType(Enum):
    HERO = "hero"
    BODY = "body"
    CTA = "cta"
    FAQ = "faq"
    PS = "ps"
    CALLOUT = "callout"
    BRIDGE = "bridge"
    COMPARISON = "comparison"


@dataclass
class Section:
    type: SectionType
    raw_md: str
    html: str = ""
    heading: str = ""
    subtitle: str = ""
    cta_text: str = ""
    cta_subtext: str = ""
    cta_structured: dict | None = None
    faq_items: list = field(default_factory=list)
    comparison_data: dict = field(default_factory=dict)
    index: int = 0


# --- Regex patterns ---

RE_H1 = re.compile(r"^#\s+(.+)$", re.MULTILINE)
RE_H3 = re.compile(r"^###\s+(?!\[)(.+)$", re.MULTILINE)
RE_CTA = re.compile(r"^###\s+\[(.+)\]\s*$", re.MULTILINE)
RE_FAQ_Q = re.compile(r'^\*\*[«"„](.+?)[»""]\*\*\s*$', re.MULTILINE)
RE_PS = re.compile(r"^(P\.S\.|P\.P\.S\.|P\.S\.S\.)\s+", re.MULTILINE)
RE_CALLOUT = re.compile(r"^\*\((.+)\)\*\s*$", re.MULTILINE)
RE_COMPARISON = re.compile(r"\*\*ChatGPT\*\*.*?\*\*М\.О\.С\.", re.DOTALL)
RE_H2 = re.compile(r"^##\s+(.+)$", re.MULTILINE)
RE_FEATURE_GRID = re.compile(
    r"<!--\s*feature-grid\s*-->\s*(.+?)\s*<!--\s*/feature-grid\s*-->",
    re.DOTALL,
)
RE_BOLD_ITEM = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
RE_CHOICE_A = re.compile(r"^Вариант\s+[АA]:", re.MULTILINE)
RE_CHOICE_B = re.compile(r"^Вариант\s+[БB]:", re.MULTILINE)
RE_RISK_A = re.compile(r"^Риск\s+варианта\s+[АA]:\s*(.+)$", re.MULTILINE)
RE_RISK_B = re.compile(r"^Риск\s+варианта\s+[БB]:\s*(.+)$", re.MULTILINE)

MD = markdown.Markdown(extensions=["extra"])


def _md(text: str) -> str:
    """Convert markdown to HTML and reset parser."""
    html = MD.convert(text.strip())
    MD.reset()
    return html


# --- Parsing ---


def parse_final_md(text: str) -> list[Section]:
    """Parse final.md into typed sections."""
    raw_chunks = re.split(r"\n---\n", text.strip())
    sections = []

    for i, chunk in enumerate(raw_chunks):
        chunk = chunk.strip()
        if not chunk:
            continue

        if i == 0:
            hero, overflow = _parse_hero(chunk)
            hero.index = len(sections)
            sections.append(hero)
            if overflow:
                body = _parse_body(overflow)
                body.index = len(sections)
                sections.append(body)
            continue
        elif RE_CTA.search(chunk):
            section = _parse_cta(chunk)
        elif RE_PS.search(chunk):
            section = _parse_ps(chunk)
        elif RE_FAQ_Q.search(chunk) and len(RE_FAQ_Q.findall(chunk)) >= 2:
            section = _parse_faq(chunk)
        elif RE_CALLOUT.match(chunk):
            section = Section(type=SectionType.CALLOUT, raw_md=chunk)
        elif RE_COMPARISON.search(chunk):
            section = _parse_comparison(chunk)
        elif _is_bridge(chunk):
            section = Section(type=SectionType.BRIDGE, raw_md=chunk)
        else:
            section = _parse_body(chunk)

        section.index = len(sections)
        sections.append(section)

    return sections


def _is_bridge(chunk: str) -> bool:
    """Detect short transition sections ending with '?'."""
    text = chunk.strip()
    text_no_md = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    return len(text_no_md) < 150 and text_no_md.rstrip().endswith("?")


def _parse_hero(chunk: str) -> tuple[Section, str | None]:
    """Parse first section as hero. Returns (hero, overflow_text)."""
    section = Section(type=SectionType.HERO, raw_md=chunk)

    h1 = RE_H1.search(chunk)
    if h1:
        section.heading = h1.group(1).strip()
        chunk = chunk[: h1.start()] + chunk[h1.end() :]

    h3 = RE_H3.search(chunk)
    if h3:
        section.subtitle = h3.group(1).strip()
        chunk = chunk[: h3.start()] + chunk[h3.end() :]

    # Split into paragraphs and limit hero size
    body = chunk.strip()
    paragraphs = re.split(r"\n\n+", body)
    paragraphs = [p for p in paragraphs if p.strip()]

    if len(paragraphs) > MAX_HERO_PARAGRAPHS:
        hero_text = "\n\n".join(paragraphs[:MAX_HERO_PARAGRAPHS])
        overflow_text = "\n\n".join(paragraphs[MAX_HERO_PARAGRAPHS:])
        section.raw_md = hero_text
        return section, overflow_text

    section.raw_md = body
    return section, None


def _parse_cta(chunk: str) -> Section:
    """Parse CTA section: ### [BUTTON TEXT] + optional subtext with steps/choice."""
    match = RE_CTA.search(chunk)
    cta_text = match.group(1).strip() if match else "CTA"

    remaining = chunk[: match.start()] + chunk[match.end() :]
    remaining = remaining.strip()

    # Try to detect structured subtext patterns
    structured = None
    if remaining:
        if _has_steps(remaining):
            structured = _parse_steps(remaining)
        elif _has_choice(remaining):
            structured = _parse_choice(remaining)

    return Section(
        type=SectionType.CTA,
        raw_md=chunk,
        cta_text=cta_text,
        cta_subtext=_md(remaining) if remaining and not structured else "",
        cta_structured=structured,
    )


def _has_steps(text: str) -> bool:
    """Detect 2+ bold items with text following them (step pattern)."""
    items = RE_BOLD_ITEM.findall(text)
    return len(items) >= 2 and not RE_CHOICE_A.search(text)


def _parse_steps(text: str) -> dict:
    """Parse steps pattern: ## Heading + intro + **Title** + description pairs + outro."""
    result = {"type": "steps", "heading": "", "intro": "", "steps": [], "outro": ""}

    # Extract ## heading
    h2 = RE_H2.search(text)
    if h2:
        result["heading"] = h2.group(1).strip()
        text = text[: h2.start()] + text[h2.end() :]
        text = text.strip()

    # Split by bold items (bold on its own line)
    parts = RE_BOLD_ITEM.split(text)
    # parts: [intro_text, bold1_title, after1_text, bold2_title, after2_text, ...]

    if len(parts) >= 3:
        result["intro"] = _md(parts[0]) if parts[0].strip() else ""

        i = 1
        while i < len(parts) - 1:
            title = parts[i].strip()
            description = parts[i + 1].strip()

            if description:
                # Split description into paragraphs; last paragraph(s) that
                # are NOT followed by another bold item may be the outro
                paragraphs = re.split(r"\n\n+", description)

                # If this is the last bold item, check if trailing paragraphs
                # look like an outro (contain inline bold like **Без продажи.**)
                if i + 2 >= len(parts):
                    step_paras = []
                    outro_paras = []
                    for p in paragraphs:
                        # Paragraph starting with **...** inline (not a standalone bold line)
                        # is likely an outro/closing statement
                        if outro_paras or (
                            step_paras and re.match(r"^\*\*.+?\*\*\s+\S", p)
                        ):
                            outro_paras.append(p)
                        else:
                            step_paras.append(p)

                    result["steps"].append({
                        "title": title,
                        "text": _md("\n\n".join(step_paras)),
                    })
                    if outro_paras:
                        result["outro"] = _md("\n\n".join(outro_paras))
                else:
                    result["steps"].append({
                        "title": title,
                        "text": _md(description),
                    })
            else:
                result["outro"] = _md(f"**{title}**")

            i += 2

    return result


def _has_choice(text: str) -> bool:
    """Detect Вариант А + Вариант Б pattern."""
    return bool(RE_CHOICE_A.search(text) and RE_CHOICE_B.search(text))


def _parse_choice(text: str) -> dict:
    """Parse choice A/B pattern with optional risks and outro."""
    result = {
        "type": "choice",
        "heading": "",
        "option_a": {"label": "Вариант А", "text": "", "risk": ""},
        "option_b": {"label": "Вариант Б", "text": "", "risk": ""},
        "outro": "",
    }

    # Extract ## heading
    h2 = RE_H2.search(text)
    if h2:
        result["heading"] = h2.group(1).strip()
        text = text[: h2.start()] + text[h2.end() :]
        text = text.strip()

    # Extract risks before splitting (they may be on separate lines)
    risk_a = RE_RISK_A.search(text)
    risk_b = RE_RISK_B.search(text)
    if risk_a:
        result["option_a"]["risk"] = risk_a.group(1).strip()
        text = text[: risk_a.start()] + text[risk_a.end() :]
    if risk_b:
        # Re-search after possible text shift
        risk_b = RE_RISK_B.search(text)
        if risk_b:
            result["option_b"]["risk"] = risk_b.group(1).strip()
            text = text[: risk_b.start()] + text[risk_b.end() :]

    text = text.strip()

    # Split into parts: before A, A content, B content, after B
    match_a = RE_CHOICE_A.search(text)
    match_b = RE_CHOICE_B.search(text)

    if match_a and match_b:
        a_start = match_a.start()
        b_start = match_b.start()

        a_text = text[a_start + len(match_a.group()):b_start].strip()
        result["option_a"]["text"] = _md(a_text)

        # Everything after Вариант Б: — split into B content and outro
        after_b = text[b_start + len(match_b.group()):].strip()
        paragraphs = re.split(r"\n\n+", after_b)
        if paragraphs:
            result["option_b"]["text"] = _md(paragraphs[0])
            if len(paragraphs) > 1:
                result["outro"] = _md("\n\n".join(paragraphs[1:]))

    return result


def _parse_faq(chunk: str) -> Section:
    """Parse FAQ section: heading + **«Question»** / answer pairs."""
    section = Section(type=SectionType.FAQ, raw_md=chunk)

    h3 = RE_H3.search(chunk)
    if h3:
        section.heading = h3.group(1).strip()
        chunk = chunk[: h3.start()] + chunk[h3.end() :]

    items = []
    parts = RE_FAQ_Q.split(chunk.strip())
    # parts: [preamble, q1, a1, q2, a2, ...]
    for j in range(1, len(parts) - 1, 2):
        question = parts[j].strip()
        answer = parts[j + 1].strip() if j + 1 < len(parts) else ""
        items.append((question, _md(answer)))

    section.faq_items = items
    return section


def _parse_comparison(chunk: str) -> Section:
    """Parse comparison section: ChatGPT vs М.О.С. with two quotes."""
    section = Section(type=SectionType.COMPARISON, raw_md=chunk)

    h3 = RE_H3.search(chunk)
    if h3:
        section.heading = h3.group(1).strip()
        chunk = chunk[: h3.start()] + chunk[h3.end() :]

    lines = chunk.strip().split("\n")
    intro, bad_lines, good_lines, conclusion = [], [], [], []

    state = "intro"
    for line in lines:
        if re.match(r"\*\*ChatGPT\*\*", line):
            state = "bad"
            bad_lines.append(line)
        elif re.match(r"\*\*М\.О\.С\.", line):
            state = "good"
            good_lines.append(line)
        elif state == "intro":
            intro.append(line)
        elif state == "bad":
            if line.strip() == "":
                state = "gap"
            else:
                bad_lines.append(line)
        elif state == "gap":
            if re.match(r"\*\*М\.О\.С\.", line):
                state = "good"
                good_lines.append(line)
            else:
                conclusion.append(line)
                state = "conclusion"
        elif state == "good":
            if line.strip() == "":
                state = "conclusion"
            else:
                good_lines.append(line)
        elif state == "conclusion":
            conclusion.append(line)

    section.comparison_data = {
        "intro": _md("\n".join(intro)),
        "bad": _md("\n".join(bad_lines)),
        "good": _md("\n".join(good_lines)),
        "conclusion": _md("\n".join(conclusion)),
    }
    return section


RE_HTML_TABLE = re.compile(
    r"<table>\s*<thead>.*?</thead>\s*<tbody>.*?</tbody>\s*</table>",
    re.DOTALL,
)


def _table_to_feature_grid(html: str) -> str:
    """Convert HTML <table> to feature-grid cards.

    Expects a table with a header row (column names) and body rows
    (row label + values per column). Transposes rows into cards
    (one card per column). Last column gets highlight.
    """
    from html.parser import HTMLParser

    class TableParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.headers = []       # column headers
            self.rows = []          # list of (row_label, [values...])
            self._in_thead = False
            self._in_tbody = False
            self._in_th = False
            self._in_td = False
            self._current_row = []
            self._current_text = ""

        def handle_starttag(self, tag, attrs):
            if tag == "thead":
                self._in_thead = True
            elif tag == "tbody":
                self._in_tbody = True
            elif tag == "th":
                self._in_th = True
                self._current_text = ""
            elif tag == "td":
                self._in_td = True
                self._current_text = ""
            elif tag == "tr":
                self._current_row = []

        def handle_endtag(self, tag):
            if tag == "thead":
                self._in_thead = False
            elif tag == "tbody":
                self._in_tbody = False
            elif tag == "th":
                self._in_th = False
                if self._in_thead:
                    self.headers.append(self._current_text.strip())
            elif tag == "td":
                self._in_td = False
                self._current_row.append(self._current_text.strip())
            elif tag == "tr":
                if self._in_tbody and self._current_row:
                    label = self._current_row[0] if self._current_row else ""
                    values = self._current_row[1:] if len(self._current_row) > 1 else []
                    self.rows.append((label, values))

        def handle_data(self, data):
            if self._in_th or self._in_td:
                self._current_text += data

    parser = TableParser()
    parser.feed(html)

    headers = parser.headers
    rows = parser.rows

    # Need at least 2 data columns (skip first empty/label header)
    data_headers = [h for h in headers if h.strip()]
    if len(data_headers) < 2:
        return html  # Not enough columns, keep as table

    # Transpose: one card per data column
    # headers[0] is row-label column (often empty), headers[1:] are card titles
    cards = []
    for col_idx, col_header in enumerate(headers[1:], start=0):
        items = []
        for row_label, values in rows:
            value = values[col_idx] if col_idx < len(values) else ""
            items.append((row_label, value))
        cards.append((col_header, items))

    if not cards:
        return html

    html_parts = ['<div class="feature-grid">']
    for idx, (title, items) in enumerate(cards):
        is_highlight = idx == len(cards) - 1
        cls = "feature-card feature-card--highlight" if is_highlight else "feature-card"
        html_parts.append(f'<div class="{cls}">')
        html_parts.append(f'<div class="feature-card__title">{title}</div>')
        html_parts.append('<dl class="feature-card__list">')
        for label, value in items:
            html_parts.append(f"<dt>{label}</dt>")
            html_parts.append(f"<dd>{value}</dd>")
        html_parts.append("</dl>")
        html_parts.append("</div>")
    html_parts.append("</div>")

    return "\n".join(html_parts)


def _parse_feature_grid(block: str) -> str:
    """Parse feature-grid block into HTML cards."""
    cards = []
    current_title = None
    current_items = []

    for line in block.strip().splitlines():
        line = line.strip()
        # Card title: **Title**
        m = re.match(r"^\*\*(.+?)\*\*$", line)
        if m:
            if current_title is not None:
                cards.append((current_title, current_items))
            current_title = m.group(1)
            current_items = []
        elif line.startswith("- ") and current_title is not None:
            # Parse "- Label: Value"
            text = line[2:]
            if ": " in text:
                label, value = text.split(": ", 1)
                current_items.append((label.strip(), value.strip()))
            else:
                current_items.append(("", text.strip()))

    if current_title is not None:
        cards.append((current_title, current_items))

    if not cards:
        return ""

    # Determine which card is the "winner" (last one gets highlight)
    html_parts = ['<div class="feature-grid">']
    for idx, (title, items) in enumerate(cards):
        is_highlight = idx == len(cards) - 1
        cls = "feature-card feature-card--highlight" if is_highlight else "feature-card"
        html_parts.append(f'<div class="{cls}">')
        html_parts.append(f'<div class="feature-card__title">{title}</div>')
        html_parts.append('<dl class="feature-card__list">')
        for label, value in items:
            html_parts.append(f"<dt>{label}</dt>")
            html_parts.append(f"<dd>{value}</dd>")
        html_parts.append("</dl>")
        html_parts.append("</div>")
    html_parts.append("</div>")

    return "\n".join(html_parts)


def _parse_ps(chunk: str) -> Section:
    """Parse P.S. / P.P.S. section."""
    return Section(type=SectionType.PS, raw_md=chunk)


def _parse_body(chunk: str) -> Section:
    """Parse regular body section with optional ### heading."""
    section = Section(type=SectionType.BODY, raw_md=chunk)

    h3 = RE_H3.search(chunk)
    if h3:
        section.heading = h3.group(1).strip()
        chunk = chunk[: h3.start()] + chunk[h3.end() :]
        section.raw_md = chunk.strip()

    return section


# --- Rendering ---


def render_sections(sections: list[Section]) -> list[Section]:
    """Convert raw markdown of each section to HTML."""
    for section in sections:
        if section.type in (SectionType.FAQ, SectionType.CTA, SectionType.COMPARISON):
            continue

        raw = section.raw_md

        # Replace feature-grid blocks with card HTML before markdown conversion
        def _replace_grid(m: re.Match) -> str:
            return _parse_feature_grid(m.group(1))

        if RE_FEATURE_GRID.search(raw):
            # Split around feature-grid, convert markdown parts, insert grid HTML
            parts = RE_FEATURE_GRID.split(raw)
            # parts: [before, grid_content, after, ...]
            html_parts = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular markdown
                    if part.strip():
                        html_parts.append(_md(part))
                else:
                    # Feature grid content
                    html_parts.append(_parse_feature_grid(part))
            section.html = "\n".join(html_parts)
        else:
            section.html = _md(raw)

        # Auto-convert any remaining <table> to feature-grid cards
        if RE_HTML_TABLE.search(section.html):
            section.html = RE_HTML_TABLE.sub(
                lambda m: _table_to_feature_grid(m.group(0)),
                section.html,
            )

    return sections


# --- Build ---


def build(project: str, input_file: str, cta_url: str, title: str | None, cta_label: str = "Записаться"):
    """Build HTML landing page from project markdown."""
    md_path = PROJECTS_DIR / project / input_file
    if not md_path.exists():
        print(f"ERROR: {md_path} not found")
        return

    text = md_path.read_text(encoding="utf-8")

    # Parse and render
    sections = parse_final_md(text)
    sections = render_sections(sections)

    # Extract title from hero heading
    page_title = title
    if not page_title:
        for s in sections:
            if s.type == SectionType.HERO and s.heading:
                page_title = s.heading
                break
    if not page_title:
        page_title = project

    # Load template
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("landing.html")

    html = template.render(
        title=page_title,
        sections=sections,
        cta_url=cta_url,
        cta_label=cta_label,
    )

    # Write output
    out_dir = DOCS_DIR / project
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"OK: {out_path.relative_to(PROJECT_ROOT)}")
    print(f"    Sections: {len(sections)}")
    for s in sections:
        print(f"    [{s.index}] {s.type.value}: {s.heading or '(no heading)'}")
    print(f"    Title: {page_title}")


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(
        description="Build HTML landing page from final.md"
    )
    parser.add_argument("project", help="Project slug (folder name in projects/)")
    parser.add_argument(
        "--input", default="final.md", help="Markdown file name (default: final.md)"
    )
    parser.add_argument(
        "--cta-url", default="#", help="URL for CTA buttons (default: #)"
    )
    parser.add_argument("--title", default=None, help="Override page <title>")
    parser.add_argument(
        "--cta-label",
        default="Записаться",
        help="Label for sticky CTA and bridge buttons (default: Записаться)",
    )
    args = parser.parse_args()

    build(args.project, args.input, args.cta_url, args.title, args.cta_label)


if __name__ == "__main__":
    main()
