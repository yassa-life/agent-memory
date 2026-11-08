"""Build a lightweight, project-local file relationship graph.

Only import/include/link syntax is inspected. File contents are never stored in
memory; the result contains paths, metadata, hashes, and resolved relationships.
"""

from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

TEXT_EXTENSIONS = {
    ".c", ".cc", ".cpp", ".cs", ".css", ".go", ".h", ".hpp", ".html",
    ".java", ".js", ".jsx", ".json", ".kt", ".kts", ".md", ".mjs",
    ".php", ".py", ".rb", ".rs", ".scss", ".svelte", ".swift", ".toml",
    ".ts", ".tsx", ".vue", ".xml", ".yaml", ".yml",
}
LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin", ".cs": "C#",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".c": "C", ".h": "C", ".cc": "C++",
    ".cpp": "C++", ".hpp": "C++", ".html": "HTML", ".css": "CSS",
    ".scss": "SCSS", ".vue": "Vue", ".svelte": "Svelte", ".md": "Markdown",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
}
SOURCE_SUFFIXES = ("", ".py", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".json", ".css", ".scss", ".html", ".vue", ".svelte", ".md")
INDEX_NAMES = ("index.py", "index.js", "index.jsx", "index.ts", "index.tsx", "__init__.py")

PATTERNS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "python": [
        ("import", re.compile(r"^\s*from\s+\.+\s+import\s+([\w]+)", re.MULTILINE)),
        ("import", re.compile(r"^\s*from\s+([.\w]+)\s+import\s+", re.MULTILINE)),
        ("import", re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE)),
    ],
    "javascript": [
        ("import", re.compile(r"(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?[\"']([^\"']+)[\"']")),
        ("require", re.compile(r"require\(\s*[\"']([^\"']+)[\"']\s*\)")),
        ("dynamic-import", re.compile(r"import\(\s*[\"']([^\"']+)[\"']\s*\)")),
    ],
    "markup": [
        ("asset", re.compile(r"(?:src|href)\s*=\s*[\"']([^\"'#?]+)[\"']", re.IGNORECASE)),
    ],
    "css": [
        ("import", re.compile(r"@import\s+(?:url\()?\s*[\"']?([^\"')\s]+)", re.IGNORECASE)),
        ("asset", re.compile(r"url\(\s*[\"']?([^\"')]+)", re.IGNORECASE)),
    ],
    "markdown": [
        ("link", re.compile(r"!?\[[^\]]*\]\(([^)#?\s]+)")),
    ],
    "java": [
        ("import", re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+);", re.MULTILINE)),
    ],
    "c-family": [
        ("include", re.compile(r"^\s*#include\s*[\"<]([^\">]+)[\">]", re.MULTILINE)),
    ],
}


def _family(extension: str) -> str | None:
    if extension == ".py": return "python"
    if extension in {".js", ".jsx", ".mjs", ".ts", ".tsx", ".vue", ".svelte"}: return "javascript"
    if extension in {".html", ".xml"}: return "markup"
    if extension in {".css", ".scss"}: return "css"
    if extension == ".md": return "markdown"
    if extension in {".java", ".kt", ".kts"}: return "java"
    if extension in {".c", ".cc", ".cpp", ".h", ".hpp"}: return "c-family"
    return None


def content_signature(path: Path, full_hash_limit: int = 2_000_000) -> str:
    digest = hashlib.sha256()
    try:
        stat = path.stat()
        with path.open("rb") as handle:
            if stat.st_size <= full_hash_limit:
                for chunk in iter(lambda: handle.read(131072), b""):
                    digest.update(chunk)
            else:
                digest.update(f"{stat.st_size}:{stat.st_mtime_ns}".encode())
                digest.update(handle.read(65536))
                handle.seek(max(0, stat.st_size - 65536))
                digest.update(handle.read(65536))
    except OSError:
        stat = path.stat()
        digest.update(f"{stat.st_size}:{stat.st_mtime_ns}".encode())
    return digest.hexdigest()[:16]


def scan_file_records(root: Path, patterns: Iterable[str], ignored_fn, max_files: int) -> tuple[list[dict[str, Any]], bool]:
    files: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        rel_dir = "" if current_path == root else current_path.relative_to(root).as_posix()
        dirnames[:] = sorted(d for d in dirnames if not ignored_fn(f"{rel_dir}/{d}".strip("/"), d, patterns))
        for filename in sorted(filenames):
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            if ignored_fn(relative, filename, patterns):
                continue
            try:
                stat = path.stat()
                suffix = path.suffix.lower()
                files.append({
                    "path": relative,
                    "name": filename,
                    "extension": suffix,
                    "language": LANGUAGES.get(suffix, suffix.lstrip(".").upper() or "File"),
                    "module": relative.split("/", 1)[0] if "/" in relative else "root",
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                    "signature": content_signature(path),
                })
            except OSError:
                continue
            if len(files) >= max_files:
                return files, True
    return files, False


def _candidate_paths(source: str, reference: str) -> list[str]:
    reference = reference.strip().replace("\\", "/")
    if not reference or reference.startswith(("http://", "https://", "data:", "mailto:", "#")):
        return []
    reference = reference.split("?", 1)[0].split("#", 1)[0]
    source_parent = PurePosixPath(source).parent
    candidates: list[PurePosixPath] = []
    if reference.startswith("/"):
        base = PurePosixPath(reference.lstrip("/"))
    elif reference.startswith("."):
        leading_dots = len(reference) - len(reference.lstrip("."))
        module_reference = reference.lstrip(".").replace(".", "/")
        base_parent = source_parent
        for _ in range(max(0, leading_dots - 1)):
            base_parent = base_parent.parent
        base = base_parent / module_reference
    else:
        base = PurePosixPath(reference)
        candidates.append(source_parent / reference)
    candidates.append(base)
    if "." in reference and not reference.startswith(".") and "/" not in reference:
        candidates.append(PurePosixPath(reference.replace(".", "/")))
    results: list[str] = []
    for candidate in candidates:
        normalized_parts: list[str] = []
        for part in candidate.parts:
            if part in {"", "."}: continue
            if part == "..":
                if normalized_parts: normalized_parts.pop()
            else: normalized_parts.append(part)
        normalized = PurePosixPath(*normalized_parts)
        if normalized.suffix:
            results.append(normalized.as_posix())
        else:
            results.extend((PurePosixPath(str(normalized) + suffix).as_posix() for suffix in SOURCE_SUFFIXES))
            results.extend(((normalized / index).as_posix() for index in INDEX_NAMES))
    return list(dict.fromkeys(results))


def build_graph(root: Path, files: list[dict[str, Any]], max_read_bytes: int = 1_000_000) -> dict[str, Any]:
    known = {item["path"] for item in files}
    basename_index: dict[str, list[str]] = {}
    for path in known:
        basename_index.setdefault(PurePosixPath(path).name, []).append(path)
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    connection_counts = {path: 0 for path in known}
    for item in files:
        source = item["path"]
        family = _family(item["extension"])
        if not family or item["size_bytes"] > max_read_bytes:
            continue
        try:
            content = (root / source).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for kind, pattern in PATTERNS[family]:
            for match in pattern.finditer(content):
                reference = match.group(1).strip()
                target = next((candidate for candidate in _candidate_paths(source, reference) if candidate in known), None)
                if not target:
                    basename = PurePosixPath(reference.replace("\\", "/")).name
                    matches = basename_index.get(basename, [])
                    if len(matches) == 1:
                        target = matches[0]
                if not target or target == source:
                    continue
                key = (source, target, kind)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"source": source, "target": target, "kind": kind})
                connection_counts[source] += 1
                connection_counts[target] += 1
    nodes = [{
        "id": item["path"], "label": item["name"], "path": item["path"],
        "module": item["module"], "language": item["language"],
        "extension": item["extension"], "size_bytes": item["size_bytes"],
        "modified": item["modified"], "connections": connection_counts[item["path"]],
    } for item in files]
    return {
        "nodes": nodes,
        "edges": sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["kind"])),
        "summary": {
            "node_count": len(nodes), "edge_count": len(edges),
            "connected_files": sum(1 for count in connection_counts.values() if count),
            "isolated_files": sum(1 for count in connection_counts.values() if not count),
        },
    }


def related_files(graph: dict[str, Any], path: str, depth: int = 1) -> dict[str, Any]:
    path = path.replace("\\", "/").lstrip("./")
    nodes = {node["id"]: node for node in graph.get("nodes", [])}
    if path not in nodes:
        matches = [node_id for node_id in nodes if node_id.endswith(path)]
        if len(matches) == 1:
            path = matches[0]
        else:
            return {"file": path, "found": False, "matches": matches[:20], "relations": []}
    visited = {path}
    frontier = {path}
    relations: list[dict[str, Any]] = []
    for level in range(1, max(1, depth) + 1):
        next_frontier: set[str] = set()
        for edge in graph.get("edges", []):
            if edge["source"] in frontier or edge["target"] in frontier:
                neighbor = edge["target"] if edge["source"] in frontier else edge["source"]
                relations.append({**edge, "depth": level})
                if neighbor not in visited:
                    next_frontier.add(neighbor)
        visited.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break
    unique = list({(item["source"], item["target"], item["kind"]): item for item in relations}.values())
    return {"file": path, "found": True, "node": nodes[path], "related_nodes": [nodes[node_id] for node_id in sorted(visited - {path})], "relations": unique}
