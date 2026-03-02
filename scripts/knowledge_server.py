#!/usr/bin/env python3
"""Copycraft Knowledge Base MCP Server.

Provides semantic search over knowledge/ directory using ChromaDB
and multilingual sentence embeddings.

Heavy components (embedding model, ChromaDB) are lazy-loaded on first
tool call to ensure fast MCP server startup.
"""

import hashlib
import json
import logging
import os
import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Suppress noisy logs from sentence-transformers and httpx during model load
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

# Suppress tqdm progress bars that flood stderr and can cause MCP pipe issues
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("NO_COLOR", "1")

# --- Configuration ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
CHROMA_DIR = PROJECT_ROOT / "chroma_data"
HASH_FILE = CHROMA_DIR / ".file_hashes.json"
COLLECTION_NAME = "knowledge"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# --- Lazy-loaded globals ---

_collection = None
_initialized = False


def _ensure_initialized():
    """Load embedding model, ChromaDB, and run startup indexing.

    No error caching — retries on every call until successful.
    """
    global _collection, _initialized
    if _initialized:
        return
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

        embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
        )
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
        stats = index_knowledge(_collection)
        print(f"Init complete. Indexing: {stats}", file=sys.stderr)
        _initialized = True
    except Exception as exc:
        msg = f"Knowledge base init failed: {exc}"
        print(msg, file=sys.stderr)
        raise RuntimeError(msg) from exc


# --- Chunking ---


MAX_CHUNK_CHARS = 2000


def _assemble_chunks(pieces: list[str], separator: str, heading: str,
                      source_file: str, category: str) -> list[dict]:
    """Group text pieces into chunks not exceeding MAX_CHUNK_CHARS."""
    sub_chunks = []
    current_buf = []
    current_len = 0

    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        piece_len = len(piece)

        if current_buf and current_len + piece_len + len(separator) > MAX_CHUNK_CHARS:
            body = separator.join(current_buf).strip()
            if body:
                part = len(sub_chunks) + 1
                sub_chunks.append({
                    "text": body,
                    "heading": f"{heading} (pt.{part})",
                    "source": source_file,
                    "category": category,
                })
            current_buf = []
            current_len = 0

        current_buf.append(piece)
        current_len += piece_len + len(separator)

    if current_buf:
        body = separator.join(current_buf).strip()
        if body:
            if sub_chunks:
                part = len(sub_chunks) + 1
                sub_chunks.append({
                    "text": body,
                    "heading": f"{heading} (pt.{part})",
                    "source": source_file,
                    "category": category,
                })
            else:
                sub_chunks.append({
                    "text": body,
                    "heading": heading,
                    "source": source_file,
                    "category": category,
                })

    return sub_chunks


def _split_large_chunk(text: str, heading: str, source_file: str, category: str) -> list[dict]:
    """Split an oversized chunk into smaller pieces.

    Strategy: try splitting by paragraphs (double newlines) first.
    If the text has no paragraph breaks, fall back to single newlines.
    """
    # Try paragraphs first
    paragraphs = re.split(r"\n{2,}", text)
    if len(paragraphs) > 1:
        return _assemble_chunks(paragraphs, "\n\n", heading, source_file, category)

    # Fallback: split by single newlines
    lines = text.split("\n")
    if len(lines) > 1:
        return _assemble_chunks(lines, "\n", heading, source_file, category)

    # Single block of text with no newlines — return as-is
    return [{
        "text": text,
        "heading": heading,
        "source": source_file,
        "category": category,
    }]


def chunk_markdown(text: str, source_file: str, category: str) -> list[dict]:
    """Split markdown text into chunks by ## and ### headings.

    Chunks larger than MAX_CHUNK_CHARS are further split by paragraphs.
    """
    chunks = []
    current_heading = source_file
    current_lines = []

    def _flush():
        if not current_lines:
            return
        body = "\n".join(current_lines).strip()
        if not body:
            return
        if len(body) > MAX_CHUNK_CHARS:
            chunks.extend(_split_large_chunk(body, current_heading, source_file, category))
        else:
            chunks.append({
                "text": body,
                "heading": current_heading,
                "source": source_file,
                "category": category,
            })

    for line in text.split("\n"):
        if re.match(r"^#{2,3}\s+", line):
            _flush()
            current_heading = line.lstrip("#").strip()
            current_lines = []
        else:
            current_lines.append(line)

    _flush()

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


@mcp_server.tool()
def search_knowledge(query: str, n_results: int = 5, category: str | None = None) -> str:
    """Search the knowledge base for relevant fragments.

    Args:
        query: Search query in natural language (Russian or English).
        n_results: Number of results to return (default 5, max 20).
        category: Filter by category: formulas, examples, expert, audience.
                  Leave empty to search all categories.
    """
    try:
        _ensure_initialized()
    except RuntimeError as exc:
        return f"ERROR: {exc}"

    n_results = min(n_results, 20)
    where = {"category": category} if category else None

    try:
        results = _collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
        )
    except Exception as exc:
        return f"ERROR: Search failed: {exc}"

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
    try:
        _ensure_initialized()
    except RuntimeError as exc:
        return f"ERROR: {exc}"

    try:
        all_data = _collection.get(include=["metadatas"])
    except Exception as exc:
        return f"ERROR: Failed to read collection: {exc}"

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
    try:
        _ensure_initialized()
    except RuntimeError as exc:
        return f"ERROR: {exc}"

    try:
        stats = index_knowledge(_collection, force=force)
    except Exception as exc:
        return f"ERROR: Reindex failed: {exc}"

    return (
        f"Reindex complete. "
        f"Indexed: {stats['indexed']}, "
        f"Skipped (unchanged): {stats['skipped']}, "
        f"Removed (deleted files): {stats['removed']}"
    )


if __name__ == "__main__":
    # Eager init: load model and index before accepting MCP requests.
    # This prevents timeouts on the first tool call.
    try:
        _ensure_initialized()
    except RuntimeError:
        pass  # Error already logged; tools will retry on each call
    mcp_server.run()
