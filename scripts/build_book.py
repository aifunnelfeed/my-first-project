#!/usr/bin/env python3
"""Build a single HTML book from markdown chapters in book/ folder."""

import markdown
from pathlib import Path
import re

BOOK_DIR = Path(__file__).parent.parent / "book"
OUTPUT = Path(__file__).parent.parent / "docs" / "book" / "index.html"

CHAPTERS = [
    "00_intro.md",
    "01_brief.md",
    "02_research.md",
    "03_strategy.md",
    "04_architecture.md",
    "05_headline.md",
    "06_lead_engagement.md",
    "07_lead_problem.md",
    "08_story.md",
    "09_mechanism.md",
    "10_product_reveal.md",
    "11_offer_close.md",
    "12_proof.md",
    "13_debugging.md",
    "14_knowledge_base.md",
]

CHAPTER_TITLES = [
    ("intro", "Введение"),
    ("ch1", "Глава 1. Бриф"),
    ("ch2", "Глава 2. Исследование"),
    ("ch3", "Глава 3. Стратегия"),
    ("ch4", "Глава 4. Архитектура"),
    ("ch5", "Глава 5. Заголовок"),
    ("ch6", "Глава 6. Лид: Вовлечение"),
    ("ch7", "Глава 7. Лид: Мост к проблеме"),
    ("ch8", "Глава 8. История"),
    ("ch9", "Глава 9. Механизм"),
    ("ch10", "Глава 10. Раскрытие продукта"),
    ("ch11", "Глава 11. Оффер и закрытие"),
    ("ch12", "Глава 12. Доказательства"),
    ("ch13", "Глава 13. Отладка"),
    ("ch14", "Глава 14. База знаний"),
]

BOOK_TITLE = "Архитектура убеждения"
BOOK_SUBTITLE = "От чистого листа до продающего текста"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {subtitle}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f4f4f5;
  --bg-card: #ffffff;
  --text: #09090b;
  --text-secondary: #71717a;
  --text-muted: #a1a1aa;
  --accent: #18181b;
  --accent-hover: #27272a;
  --border: #e4e4e7;
  --code-bg: #f4f4f5;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -2px rgba(0,0,0,0.05);
  --radius: 12px;
  --radius-sm: 8px;
  --sidebar-w: 260px;
  --table-bg: #f0f4ff;
  --table-header: #dbe4f8;
  --table-header-text: #3b4f74;
  --table-border: #c7d4ec;
  --table-stripe: #e8edf8;
}}

html.dark {{
  --bg: #09090b;
  --bg-card: #18181b;
  --text: #fafafa;
  --text-secondary: #a1a1aa;
  --text-muted: #71717a;
  --accent: #fafafa;
  --accent-hover: #e4e4e7;
  --border: #27272a;
  --code-bg: #27272a;
  --shadow: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-lg: 0 4px 6px -1px rgba(0,0,0,0.4);
  --table-bg: #141829;
  --table-header: #1c2240;
  --table-header-text: #8b9fce;
  --table-border: #2a3358;
  --table-stripe: #181d33;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  transition: background 0.3s, color 0.3s;
}}

/* --- Sidebar --- */
.sidebar {{
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-w);
  height: 100vh;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 1.5rem 0;
  z-index: 300;
  transition: transform 0.3s ease;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}}

.sidebar::-webkit-scrollbar {{
  width: 4px;
}}

.sidebar::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 4px;
}}

.sidebar-header {{
  padding: 0.5rem 1.25rem 1.25rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0.75rem;
}}

.sidebar-header .book-title {{
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.3;
}}

.sidebar-header .book-subtitle {{
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}}

.sidebar-nav {{
  list-style: none;
}}

.sidebar-nav li a {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.45rem 1.25rem;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.15s;
  border-left: 2px solid transparent;
}}

.sidebar-nav li a:hover {{
  color: var(--text);
  background: var(--bg);
}}

html.dark .sidebar-nav li a:hover {{
  background: var(--code-bg);
}}

.sidebar-nav li a.active {{
  color: var(--text);
  background: var(--bg);
  border-left-color: var(--text);
  font-weight: 600;
}}

html.dark .sidebar-nav li a.active {{
  background: var(--code-bg);
}}

.sidebar-nav li a .snum {{
  font-size: 0.7rem;
  color: var(--text-muted);
  min-width: 1.25rem;
  text-align: right;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}}

.sidebar-bottom {{
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border);
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
}}

.sidebar-bottom button {{
  flex: 1;
  padding: 0.4rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--text);
  transition: all 0.15s;
}}

.sidebar-bottom button:hover {{
  background: var(--border);
}}

/* Mobile sidebar toggle */
.sidebar-toggle {{
  display: none;
  position: fixed;
  top: 1rem;
  left: 1rem;
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  z-index: 400;
  box-shadow: var(--shadow);
  font-size: 1.1rem;
  color: var(--text);
  transition: all 0.2s;
}}

.sidebar-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 250;
}}

/* --- Main content --- */
.main {{
  margin-left: var(--sidebar-w);
  transition: margin-left 0.3s;
}}

/* --- Cover --- */
.cover {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 4rem 2rem;
  position: relative;
  overflow: hidden;
}}

.cover::before {{
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at 30% 50%, rgba(120,119,198,0.08) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 50%, rgba(72,149,239,0.06) 0%, transparent 50%);
  pointer-events: none;
}}

html.dark .cover::before {{
  background: radial-gradient(ellipse at 30% 50%, rgba(120,119,198,0.15) 0%, transparent 50%),
              radial-gradient(ellipse at 70% 50%, rgba(72,149,239,0.1) 0%, transparent 50%);
}}

.cover h1 {{
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 0.75rem;
  position: relative;
  z-index: 1;
  line-height: 1.1;
}}

.cover .subtitle {{
  font-size: 1.25rem;
  font-weight: 400;
  color: var(--text-secondary);
  margin-bottom: 3rem;
  position: relative;
  z-index: 1;
}}

.cover .scroll-hint {{
  position: relative;
  z-index: 1;
  margin-top: 2rem;
  color: var(--text-muted);
  animation: bounce 2s ease-in-out infinite;
}}

.cover .scroll-hint svg {{
  width: 24px;
  height: 24px;
}}

@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(8px); }}
}}

/* --- TOC (inline, stays in main flow) --- */
.toc {{
  max-width: 640px;
  margin: 0 auto 3rem;
  padding: 2rem;
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}}

.toc h2 {{
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}}

.toc ol {{
  list-style: none;
}}

.toc li {{
  margin-bottom: 0;
}}

.toc li a {{
  color: var(--text);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.15s;
}}

.toc li a:hover {{
  background: var(--bg);
}}

html.dark .toc li a:hover {{
  background: var(--code-bg);
}}

.toc li a .num {{
  font-size: 0.8rem;
  color: var(--text-muted);
  min-width: 1.75rem;
  text-align: right;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}}

/* --- Chapter --- */
.chapter {{
  max-width: 720px;
  margin: 1.5rem auto;
  padding: 2.5rem 3rem;
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}}

.chapter-divider {{
  text-align: center;
  padding: 1.5rem 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  letter-spacing: 0.3rem;
}}

.chapter h1 {{
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
  line-height: 1.3;
}}

.chapter h2 {{
  font-size: 1.3rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  margin-top: 2.5rem;
  margin-bottom: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}}

.chapter h2:first-of-type {{
  border-top: none;
  padding-top: 0;
}}

.chapter h3 {{
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}}

.chapter h4 {{
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}}

.chapter p {{
  margin-bottom: 1rem;
  color: var(--text);
}}

.chapter ul, .chapter ol {{
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}}

.chapter li {{
  margin-bottom: 0.35rem;
}}

.chapter li::marker {{
  color: var(--text-muted);
}}

.chapter blockquote {{
  border-left: 3px solid var(--border);
  padding: 0.75rem 1.25rem;
  margin: 1.25rem 0;
  background: var(--bg);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}}

.chapter blockquote p:last-child {{
  margin-bottom: 0;
}}

.chapter code {{
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  font-size: 0.875em;
  font-family: 'SF Mono', 'Fira Code', 'JetBrains Mono', monospace;
}}

.chapter pre {{
  background: var(--code-bg);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 1.25rem 0;
  border: 1px solid var(--border);
}}

.chapter pre code {{
  background: none;
  padding: 0;
  font-size: 0.85rem;
  line-height: 1.6;
}}

.chapter strong {{
  font-weight: 600;
}}

.chapter em {{
  color: var(--text-secondary);
}}

.table-wrap {{
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  margin: 1.25rem 0;
  border-radius: var(--radius-sm);
  border: 1px solid var(--table-border);
  background: var(--table-bg);
}}

.chapter table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  min-width: 400px;
}}

.chapter th {{
  background: var(--table-header);
  padding: 0.6rem 0.875rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--table-header-text);
  border-bottom: 1px solid var(--table-border);
}}

.chapter td {{
  padding: 0.6rem 0.875rem;
  border-bottom: 1px solid var(--table-border);
  vertical-align: top;
}}

.chapter tr:nth-child(even) {{
  background: var(--table-stripe);
}}

.chapter tr:last-child td {{
  border-bottom: none;
}}

.chapter hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}}

/* --- Chapter pagination --- */
.chapter-nav {{
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  gap: 1rem;
  max-width: 720px;
  margin: 0 auto 1.5rem;
  padding: 0 0.5rem;
}}

.chapter-nav a {{
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  text-decoration: none;
  color: var(--text);
  transition: all 0.15s;
  min-width: 0;
  flex: 1;
  box-shadow: var(--shadow);
}}

.chapter-nav a:hover {{
  border-color: var(--text-muted);
  box-shadow: var(--shadow-lg);
}}

.chapter-nav a.next {{
  text-align: right;
  align-items: flex-end;
}}

.chapter-nav .nav-label {{
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}}

.chapter-nav .nav-title {{
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}

.chapter-nav .spacer {{
  flex: 1;
}}

/* --- Footer --- */
.footer {{
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  max-width: 720px;
  margin: 0 auto;
}}

/* --- Responsive --- */
@media (min-width: 1100px) {{
  .chapter, .chapter-nav, .toc {{
    margin-left: auto;
    margin-right: auto;
  }}
}}

@media (max-width: 1099px) {{
  .sidebar {{
    transform: translateX(-100%);
  }}
  .sidebar.open {{
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
  }}
  .sidebar-toggle {{
    display: flex;
  }}
  .sidebar-overlay.open {{
    display: block;
  }}
  .main {{
    margin-left: 0;
  }}
}}

@media (max-width: 800px) {{
  body {{ font-size: 15px; }}
  .cover h1 {{ font-size: 2.5rem; }}
  .cover .subtitle {{ font-size: 1.1rem; }}
  .chapter {{ padding: 1.75rem 1.5rem; margin: 1rem; border-radius: var(--radius-sm); }}
  .chapter-nav {{ padding: 0 1rem; }}
  .toc {{ margin: 0 1rem 2rem; padding: 1.5rem; }}
}}

@media (max-width: 500px) {{
  .cover h1 {{ font-size: 2rem; }}
  .chapter {{ padding: 1.25rem 1rem; }}
  .chapter h1 {{ font-size: 1.4rem; }}
  .chapter-nav a {{ padding: 0.75rem 1rem; }}
  .chapter-nav .nav-title {{ font-size: 0.8rem; }}
}}

/* --- Print --- */
@media print {{
  .sidebar, .sidebar-toggle, .sidebar-overlay {{ display: none !important; }}
  .main {{ margin-left: 0 !important; }}
  .cover {{ min-height: auto; page-break-after: always; }}
  .toc {{ page-break-after: always; }}
  .chapter {{ box-shadow: none; border: none; page-break-before: always; }}
  .chapter-nav {{ display: none; }}
  body {{ background: #fff; color: #000; }}
}}
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <div class="book-title">{title}</div>
    <div class="book-subtitle">{subtitle}</div>
  </div>
  <ol class="sidebar-nav" id="sidebarNav">
{sidebar}
  </ol>
  <div class="sidebar-bottom">
    <button id="themeToggle" title="Toggle theme"><span id="themeIcon">&#9789;</span></button>
  </div>
</aside>

<!-- Mobile toggle -->
<button class="sidebar-toggle" id="sidebarToggle" title="Menu">&#9776;</button>
<div class="sidebar-overlay" id="sidebarOverlay"></div>

<!-- Main -->
<div class="main" id="mainContent">

  <!-- Cover -->
  <div class="cover" id="cover">
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
    <div class="scroll-hint">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
    </div>
  </div>

  <!-- TOC -->
  <nav class="toc">
    <h2>Содержание</h2>
    <ol>
{toc}
    </ol>
  </nav>

  <!-- Chapters -->
{chapters}

  <div class="footer">
    Copycraft &mdash; Маркетинговая Операционная Система
  </div>

</div>

<script>
// Theme
const toggle = document.getElementById('themeToggle');
const icon = document.getElementById('themeIcon');
const html = document.documentElement;

function setTheme(dark) {{
  html.classList.toggle('dark', dark);
  icon.textContent = dark ? '\\u2600' : '\\u263D';
  localStorage.setItem('theme', dark ? 'dark' : 'light');
}}

const saved = localStorage.getItem('theme');
if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
  setTheme(true);
}}

toggle.addEventListener('click', () => {{
  setTheme(!html.classList.contains('dark'));
}});

// Sidebar mobile
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const overlay = document.getElementById('sidebarOverlay');

function closeSidebar() {{
  sidebar.classList.remove('open');
  overlay.classList.remove('open');
}}

sidebarToggle.addEventListener('click', () => {{
  sidebar.classList.toggle('open');
  overlay.classList.toggle('open');
}});

overlay.addEventListener('click', closeSidebar);

// Close sidebar on nav click (mobile)
document.querySelectorAll('.sidebar-nav a').forEach(a => {{
  a.addEventListener('click', () => {{
    if (window.innerWidth < 1100) closeSidebar();
  }});
}});

// Active chapter tracking
const chapters = document.querySelectorAll('.chapter');
const navLinks = document.querySelectorAll('.sidebar-nav a');
const chapterIds = Array.from(chapters).map(c => c.id);

function updateActive() {{
  let current = '';
  const scrollY = window.scrollY + 120;

  for (const ch of chapters) {{
    if (ch.offsetTop <= scrollY) {{
      current = ch.id;
    }}
  }}

  navLinks.forEach(link => {{
    const href = link.getAttribute('href').slice(1);
    link.classList.toggle('active', href === current);
  }});

  // Scroll active item into view in sidebar
  const activeLink = sidebar.querySelector('.sidebar-nav a.active');
  if (activeLink) {{
    const rect = activeLink.getBoundingClientRect();
    const sidebarRect = sidebar.getBoundingClientRect();
    if (rect.top < sidebarRect.top + 80 || rect.bottom > sidebarRect.bottom - 80) {{
      activeLink.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
    }}
  }}
}}

let ticking = false;
window.addEventListener('scroll', () => {{
  if (!ticking) {{
    requestAnimationFrame(() => {{
      updateActive();
      ticking = false;
    }});
    ticking = true;
  }}
}});

updateActive();
</script>

</body>
</html>
"""


def build():
    md = markdown.Markdown(extensions=["tables", "fenced_code", "smarty"])

    toc_lines = []
    sidebar_lines = []
    chapter_blocks = []

    # Short labels for sidebar (without "Глава N.")
    sidebar_labels = [
        "Введение",
        "1. Бриф",
        "2. Исследование",
        "3. Стратегия",
        "4. Архитектура",
        "5. Заголовок",
        "6. Лид: Вовлечение",
        "7. Лид: Проблема",
        "8. История",
        "9. Механизм",
        "10. Продукт",
        "11. Оффер",
        "12. Доказательства",
        "13. Отладка",
        "14. База знаний",
    ]

    # Collect valid chapters
    valid = []
    for i, (fname, (anchor, toc_title)) in enumerate(zip(CHAPTERS, CHAPTER_TITLES)):
        filepath = BOOK_DIR / fname
        if not filepath.exists():
            print(f"WARNING: {filepath} not found, skipping")
            continue
        valid.append((i, fname, anchor, toc_title, filepath))

    for idx, (i, fname, anchor, toc_title, filepath) in enumerate(valid):
        text = filepath.read_text(encoding="utf-8")
        md.reset()
        html = md.convert(text)
        # Wrap tables for mobile scroll
        html = html.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

        num = "—" if i == 0 else str(i)
        toc_lines.append(
            f'    <li><a href="#{anchor}"><span class="num">{num}</span>{toc_title}</a></li>'
        )

        snum = "" if i == 0 else f"{i}."
        slabel = sidebar_labels[i] if i < len(sidebar_labels) else toc_title
        sidebar_lines.append(
            f'    <li><a href="#{anchor}"><span class="snum">{snum}</span>{slabel}</a></li>'
        )

        chapter_blocks.append(f'<div class="chapter-divider">&#10044; &#10044; &#10044;</div>')
        chapter_blocks.append(f'<article class="chapter" id="{anchor}">')
        chapter_blocks.append(html)
        chapter_blocks.append("</article>")

        # Pagination nav
        nav_parts = []
        if idx > 0:
            prev_anchor = valid[idx - 1][2]
            prev_title = valid[idx - 1][3]
            nav_parts.append(
                f'<a href="#{prev_anchor}" class="prev">'
                f'<span class="nav-label">&larr; Назад</span>'
                f'<span class="nav-title">{prev_title}</span></a>'
            )
        else:
            nav_parts.append('<div class="spacer"></div>')

        if idx < len(valid) - 1:
            next_anchor = valid[idx + 1][2]
            next_title = valid[idx + 1][3]
            nav_parts.append(
                f'<a href="#{next_anchor}" class="next">'
                f'<span class="nav-label">Далее &rarr;</span>'
                f'<span class="nav-title">{next_title}</span></a>'
            )
        else:
            nav_parts.append('<div class="spacer"></div>')

        chapter_blocks.append(f'<div class="chapter-nav">{"".join(nav_parts)}</div>')

    toc_html = "\n".join(toc_lines)
    sidebar_html = "\n".join(sidebar_lines)
    chapters_html = "\n".join(chapter_blocks)

    output_html = HTML_TEMPLATE.format(
        title=BOOK_TITLE,
        subtitle=BOOK_SUBTITLE,
        toc=toc_html,
        sidebar=sidebar_html,
        chapters=chapters_html,
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output_html, encoding="utf-8")
    print(f"Book built: {OUTPUT}")
    print(f"Size: {OUTPUT.stat().st_size / 1024:.0f} KB")
    print(f"Chapters: {len(valid)}")


if __name__ == "__main__":
    build()
