#!/usr/bin/env python3
"""Convert PDF, DOCX, TXT files to Markdown for knowledge base."""

import sys
import shutil
from pathlib import Path

import pdfplumber
from docx import Document

# --- Config ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
SOURCE_DIR = Path("/Users/ilaija/Documents/Marketing files")

# File → (category, output_name)
FILE_MAP = {
    "100_Velichayshikh_prodayuschikh_pisem_Ben_Khart.pdf": ("examples", "100_greatest_sales_letters"),
    "OT_Long_Copy_1.pdf": ("examples", "ot_long_copy_1"),
    "OT_Long_Copy_2.pdf": ("examples", "ot_long_copy_2"),
    "Прорывная_реклама._Юджин_Шварц.pdf": ("formulas", "breakthrough_advertising_schwartz"),
    "MOS 2.0.docx": ("formulas", "mos_2_0"),
}


def pdf_to_md(pdf_path: Path) -> str:
    """Extract text from PDF and format as markdown."""
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                lines.append(f"## Страница {i}\n")
                lines.append(text.strip())
                lines.append("")
    return "\n".join(lines)


def docx_to_md(docx_path: Path) -> str:
    """Extract text from DOCX and format as markdown."""
    doc = Document(docx_path)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            lines.append("")
            continue
        # Convert heading styles to markdown
        if para.style and para.style.name:
            style = para.style.name.lower()
            if "heading 1" in style:
                lines.append(f"## {text}")
                continue
            elif "heading 2" in style:
                lines.append(f"### {text}")
                continue
            elif "heading 3" in style:
                lines.append(f"#### {text}")
                continue
        lines.append(text)
    return "\n".join(lines)


def convert_all():
    """Convert all files and place into knowledge/ categories."""
    for filename, (category, output_name) in FILE_MAP.items():
        source = SOURCE_DIR / filename
        if not source.exists():
            print(f"SKIP: {filename} — file not found")
            continue

        target_dir = KNOWLEDGE_DIR / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{output_name}.md"

        ext = source.suffix.lower()
        print(f"Converting: {filename} → {category}/{output_name}.md ...", end=" ")

        try:
            if ext == ".pdf":
                md_text = pdf_to_md(source)
            elif ext == ".docx":
                md_text = docx_to_md(source)
            elif ext == ".txt":
                md_text = source.read_text(encoding="utf-8")
            else:
                print(f"SKIP (unknown format: {ext})")
                continue

            # Add title
            title = output_name.replace("_", " ").title()
            md_content = f"# {title}\n\n{md_text}"

            target.write_text(md_content, encoding="utf-8")
            size_kb = target.stat().st_size / 1024
            print(f"OK ({size_kb:.1f} KB)")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\nDone! Run reindex() in MCP to update the knowledge base.")


if __name__ == "__main__":
    convert_all()
