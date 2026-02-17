#!/usr/bin/env python3
"""Copycraft Knowledge Base MCP Server.

Provides semantic search over knowledge/ directory using ChromaDB
and multilingual sentence embeddings.
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from mcp.server.fastmcp import FastMCP

# --- Configuration ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
CHROMA_DIR = PROJECT_ROOT / "chroma_data"
HASH_FILE = CHROMA_DIR / ".file_hashes.json"
COLLECTION_NAME = "knowledge"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- Chunking ---


def chunk_markdown(text: str, source_file: str, category: str) -> list[dict]:
    """Split markdown text into chunks by ## and ### headings."""
    chunks = []
    current_heading = source_file
    current_lines = []

    for line in text.split("\n"):
        if re.match(r"^#{2,3}\s+", line):
            # Save previous chunk
            if current_lines:
                body = "\n".join(current_lines).strip()
                if body:
                    chunks.append({
                        "text": body,
                        "heading": current_heading,
                        "source": source_file,
                        "category": category,
                    })
            current_heading = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last chunk
    if current_lines:
        body = "\n".join(current_lines).strip()
        if body:
            chunks.append({
                "text": body,
                "heading": current_heading,
                "source": source_file,
                "category": category,
            })

    return chunks


# --- Indexing ---


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_hashes() -> dict:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text())
    return {}


def save_hashes(hashes: dict):
    HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(json.dumps(hashes, indent=2))


def get_category(path: Path) -> str:
    """Extract category from path: knowledge/formulas/file.md -> formulas."""
    rel = path.relative_to(KNOWLEDGE_DIR)
    parts = rel.parts
    return parts[0] if len(parts) > 1 else "general"


def index_knowledge(collection, force: bool = False) -> dict:
    """Index all .md files from knowledge/ into ChromaDB.

    Returns stats: {indexed: int, skipped: int, removed: int}.
    """
    if not KNOWLEDGE_DIR.exists():
        return {"indexed": 0, "skipped": 0, "removed": 0, "error": "knowledge/ not found"}

    old_hashes = {} if force else load_hashes()
    new_hashes = {}
    stats = {"indexed": 0, "skipped": 0, "removed": 0}

    # Find all markdown files
    md_files = list(KNOWLEDGE_DIR.rglob("*.md"))

    for md_path in md_files:
        rel_path = str(md_path.relative_to(PROJECT_ROOT))
        h = file_hash(md_path)
        new_hashes[rel_path] = h

        if not force and old_hashes.get(rel_path) == h:
            stats["skipped"] += 1
            continue

        # Remove old chunks for this file
        existing = collection.get(where={"source": rel_path})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])

        # Chunk and add
        text = md_path.read_text(encoding="utf-8")
        category = get_category(md_path)
        chunks = chunk_markdown(text, rel_path, category)

        if chunks:
            collection.add(
                ids=[f"{rel_path}::{i}" for i in range(len(chunks))],
                documents=[c["text"] for c in chunks],
                metadatas=[{
                    "source": c["source"],
                    "heading": c["heading"],
                    "category": c["category"],
                } for c in chunks],
            )
        stats["indexed"] += 1

    # Remove chunks for deleted files
    for old_path in set(old_hashes.keys()) - set(new_hashes.keys()):
        existing = collection.get(where={"source": old_path})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
        stats["removed"] += 1

    save_hashes(new_hashes)
    return stats


# --- MCP Server ---

mcp_server = FastMCP(
    "copycraft-knowledge",
    instructions="Semantic search over Copycraft knowledge base (formulas, examples, expert materials, audience data).",
)

# Initialize ChromaDB
embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL,
)
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
)

# Index on startup
startup_stats = index_knowledge(collection)
print(f"Startup indexing: {startup_stats}", file=sys.stderr)


@mcp_server.tool()
def search_knowledge(query: str, n_results: int = 5, category: str | None = None) -> str:
    """Search the knowledge base for relevant fragments.

    Args:
        query: Search query in natural language (Russian or English).
        n_results: Number of results to return (default 5, max 20).
        category: Filter by category: formulas, examples, expert, audience.
                  Leave empty to search all categories.
    """
    n_results = min(n_results, 20)
    where = {"category": category} if category else None

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where,
    )

    if not results["documents"] or not results["documents"][0]:
        return "No results found."

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        relevance = max(0, round((1 - dist) * 100, 1))
        output.append(
            f"**[{meta['category']}/{meta['heading']}]** (relevance: {relevance}%)\n"
            f"Source: {meta['source']}\n\n"
            f"{doc}\n"
        )

    return "\n---\n".join(output)


@mcp_server.tool()
def list_sources() -> str:
    """List all indexed files and their chunk counts."""
    all_data = collection.get()
    if not all_data["ids"]:
        return "Knowledge base is empty. Add .md files to knowledge/ and run reindex."

    sources = {}
    for meta in all_data["metadatas"]:
        src = meta["source"]
        cat = meta["category"]
        key = f"[{cat}] {src}"
        sources[key] = sources.get(key, 0) + 1

    lines = [f"Total chunks: {len(all_data['ids'])}\n"]
    for src, count in sorted(sources.items()):
        lines.append(f"- {src}: {count} chunks")

    return "\n".join(lines)


@mcp_server.tool()
def reindex(force: bool = False) -> str:
    """Re-index all knowledge base files.

    Args:
        force: If True, re-index all files regardless of changes.
               If False (default), only re-index changed files.
    """
    stats = index_knowledge(collection, force=force)
    return (
        f"Reindex complete. "
        f"Indexed: {stats['indexed']}, "
        f"Skipped (unchanged): {stats['skipped']}, "
        f"Removed (deleted files): {stats['removed']}"
    )


if __name__ == "__main__":
    mcp_server.run()
