#!/usr/bin/env python3
"""Copycraft Research MCP Server.

Provides access to scientific papers via PubMed and Semantic Scholar APIs.
No third-party dependencies beyond httpx and MCP SDK.
"""

import asyncio
import logging
import sys

import httpx
from mcp.server.fastmcp import FastMCP

logging.getLogger("httpx").setLevel(logging.WARNING)

PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
SEMANTIC_SCHOLAR = "https://api.semanticscholar.org/graph/v1/paper/search"

TIMEOUT = 15.0

mcp_server = FastMCP(
    "copycraft-research",
    instructions="Search PubMed and Semantic Scholar for scientific papers. Use for evidence, proof elements, and mechanism validation.",
)


def _truncate(text: str, max_len: int = 500) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


@mcp_server.tool()
async def search_pubmed(query: str, max_results: int = 5) -> str:
    """Search PubMed for biomedical and life science research papers.

    Args:
        query: Search query (e.g. "vitamin D immune system meta-analysis").
        max_results: Number of results (1-15, default 5).
    """
    max_results = min(max(max_results, 1), 15)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Step 1: search for IDs
        search_resp = await client.get(PUBMED_SEARCH, params={
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        })
        search_resp.raise_for_status()
        data = search_resp.json()

        id_list = data.get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return f"PubMed: no results for '{query}'"

        total = data.get("esearchresult", {}).get("count", "?")

        # Step 2: fetch abstracts
        fetch_resp = await client.get(PUBMED_FETCH, params={
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
            "rettype": "abstract",
        })
        fetch_resp.raise_for_status()
        xml_text = fetch_resp.text

    # Parse XML manually (no lxml dependency)
    articles = _parse_pubmed_xml(xml_text)

    lines = [f"**PubMed results for:** {query} ({total} total)\n"]
    for i, art in enumerate(articles, 1):
        lines.append(
            f"### {i}. {art['title']}\n"
            f"- **Authors:** {art['authors']}\n"
            f"- **Journal:** {art['journal']} ({art['year']})\n"
            f"- **PMID:** {art['pmid']} | https://pubmed.ncbi.nlm.nih.gov/{art['pmid']}/\n"
            f"- **Abstract:** {_truncate(art['abstract'])}\n"
        )

    return "\n".join(lines)


def _parse_pubmed_xml(xml: str) -> list[dict]:
    """Minimal XML parser for PubMed efetch results. No external deps."""
    import xml.etree.ElementTree as ET

    articles = []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return articles

    for article_el in root.iter("PubmedArticle"):
        medline = article_el.find(".//MedlineCitation")
        if medline is None:
            continue

        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else ""

        art = medline.find("Article")
        if art is None:
            continue

        title_el = art.find("ArticleTitle")
        title = title_el.text if title_el is not None else "No title"

        abstract_el = art.find(".//AbstractText")
        abstract = abstract_el.text if abstract_el is not None else "No abstract available"

        journal_el = art.find(".//Journal/Title")
        journal = journal_el.text if journal_el is not None else ""

        year_el = art.find(".//PubDate/Year")
        if year_el is None:
            year_el = art.find(".//PubDate/MedlineDate")
        year = year_el.text if year_el is not None else ""

        author_list = art.find("AuthorList")
        authors = []
        if author_list is not None:
            for author in author_list.findall("Author"):
                last = author.find("LastName")
                init = author.find("Initials")
                if last is not None:
                    name = last.text
                    if init is not None:
                        name += f" {init.text}"
                    authors.append(name)
        author_str = ", ".join(authors[:5])
        if len(authors) > 5:
            author_str += " et al."

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "year": year,
            "authors": author_str or "N/A",
        })

    return articles


@mcp_server.tool()
async def search_semantic_scholar(query: str, max_results: int = 5, year: str | None = None) -> str:
    """Search Semantic Scholar for academic papers across all fields.

    Args:
        query: Search query (e.g. "cognitive biases in purchasing decisions").
        max_results: Number of results (1-15, default 5).
        year: Filter by year range (e.g. "2020-2025" or "2023").
    """
    max_results = min(max(max_results, 1), 15)

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,authors,year,citationCount,journal,externalIds,url",
    }
    if year:
        params["year"] = year

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(3):
            resp = await client.get(SEMANTIC_SCHOLAR, params=params)
            if resp.status_code == 429:
                wait = 2 ** attempt
                print(f"Semantic Scholar rate limit, retry in {wait}s...", file=sys.stderr)
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            break
        else:
            return f"Semantic Scholar: rate limited after 3 retries for '{query}'"
        data = resp.json()

    papers = data.get("data", [])
    if not papers:
        return f"Semantic Scholar: no results for '{query}'"

    total = data.get("total", "?")
    lines = [f"**Semantic Scholar results for:** {query} ({total} total)\n"]

    for i, paper in enumerate(papers, 1):
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        author_str = ", ".join(authors[:5])
        if len(authors) > 5:
            author_str += " et al."

        journal_info = paper.get("journal", {})
        journal_name = journal_info.get("name", "") if journal_info else ""

        ext_ids = paper.get("externalIds", {}) or {}
        doi = ext_ids.get("DOI", "")
        doi_link = f"https://doi.org/{doi}" if doi else ""

        pmid = ext_ids.get("PubMed", "")
        arxiv = ext_ids.get("ArXiv", "")

        ids_parts = []
        if doi_link:
            ids_parts.append(f"DOI: {doi_link}")
        if pmid:
            ids_parts.append(f"PMID: {pmid}")
        if arxiv:
            ids_parts.append(f"arXiv: {arxiv}")
        ids_str = " | ".join(ids_parts) if ids_parts else paper.get("url", "")

        abstract = paper.get("abstract") or "No abstract available"

        lines.append(
            f"### {i}. {paper.get('title', 'No title')}\n"
            f"- **Authors:** {author_str or 'N/A'}\n"
            f"- **Journal:** {journal_name or 'N/A'} ({paper.get('year', '?')})\n"
            f"- **Citations:** {paper.get('citationCount', '?')}\n"
            f"- **IDs:** {ids_str}\n"
            f"- **Abstract:** {_truncate(abstract)}\n"
        )

    return "\n".join(lines)


@mcp_server.tool()
async def search_papers(query: str, max_results: int = 5) -> str:
    """Search both PubMed and Semantic Scholar simultaneously.

    Best for comprehensive research — returns combined results from both sources.

    Args:
        query: Search query in natural language.
        max_results: Results per source (1-10, default 5).
    """
    max_results = min(max(max_results, 1), 10)

    results = []
    errors = []

    # PubMed
    try:
        pubmed_result = await search_pubmed(query, max_results)
        results.append(pubmed_result)
    except Exception as e:
        errors.append(f"PubMed error: {e}")

    # Semantic Scholar
    try:
        ss_result = await search_semantic_scholar(query, max_results)
        results.append(ss_result)
    except Exception as e:
        errors.append(f"Semantic Scholar error: {e}")

    if errors:
        results.append("\n**Errors:**\n" + "\n".join(errors))

    return "\n\n---\n\n".join(results)


if __name__ == "__main__":
    print("Research MCP server starting...", file=sys.stderr)
    mcp_server.run()
