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
    """Parse CTA section: ### [BUTTON TEXT] + optional subtext."""
    match = RE_CTA.search(chunk)
    cta_text = match.group(1).strip() if match else "CTA"

    remaining = chunk[: match.start()] + chunk[match.end() :]
    remaining = remaining.strip()

    return Section(
        type=SectionType.CTA,
        raw_md=chunk,
        cta_text=cta_text,
        cta_subtext=remaining,
    )


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
        section.html = _md(section.raw_md)

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
