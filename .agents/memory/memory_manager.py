"""Agent Memory: dependency-free project memory for any coding agent."""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

MEMORY_DIR = Path(__file__).resolve().parent
if str(MEMORY_DIR) not in sys.path:
    sys.path.insert(0, str(MEMORY_DIR))

from relation_graph import build_graph, related_files, scan_file_records

SCHEMA_VERSION = 3
HISTORY_LIMIT = 100
DEFAULT_IGNORES = {".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "node_modules", "dist", "build", "coverage", "__pycache__", ".pytest_cache", ".mypy_cache", ".next", ".nuxt", "target", "vendor"}
GENERATED_FILES = {".agents/memory/memory.json", ".agents/memory/context.md", ".agents/memory/visualizer.html"}
STACK_MARKERS = {"package.json": "Node.js / JavaScript", "pyproject.toml": "Python", "requirements.txt": "Python", "pom.xml": "Java / Maven", "build.gradle": "Java / Gradle", "build.gradle.kts": "Kotlin / Gradle", "Cargo.toml": "Rust", "go.mod": "Go", "composer.json": "PHP", "Gemfile": "Ruby", "pubspec.yaml": "Dart / Flutter", "*.sln": ".NET", "*.csproj": ".NET"}
ENTRYPOINT_NAMES = {"main.py", "app.py", "server.py", "manage.py", "index.js", "index.ts", "main.js", "main.ts", "main.tsx", "App.tsx", "Program.cs", "Main.java", "Dockerfile", "docker-compose.yml", "docker-compose.yaml"}
AGENT_INSTRUCTIONS = """## Agent Memory

Read `.agents/memory/context.md` before broad repository exploration. Use `python .agents/memory/memory_manager.py related "path/to/file"` to find linked files without scanning the whole project. Verify relevant source before editing. After meaningful changes, run `python .agents/memory/memory_manager.py scan`. Never store secrets or private chat content in memory.
"""
AGENT_ADAPTERS = {
    "codex": ("Codex", "AGENTS.md"),
    "antigravity": ("Antigravity", "GEMINI.md"),
    "gemini": ("Gemini", "GEMINI.md"),
    "claude": ("Claude", "CLAUDE.md"),
    "cursor": ("Cursor", ".cursor/rules/agent-memory.mdc"),
    "copilot": ("GitHub Copilot", ".github/copilot-instructions.md"),
    "windsurf": ("Windsurf", ".windsurf/rules/agent-memory.md"),
    "hermes": ("Hermes", "HERMES.md"),
}
DETECTION_MARKERS = {name: Path(path) for name, (_, path) in AGENT_ADAPTERS.items()}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def memory_paths(root: Path) -> tuple[Path, Path, Path]:
    directory = root / ".agents" / "memory"
    return directory / "memory.json", directory / "context.md", directory / "visualizer.html"


def load_memory(root: Path) -> dict[str, Any]:
    store, _, _ = memory_paths(root)
    if not store.exists(): return {}
    try:
        data = json.loads(store.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {store}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def save_memory(root: Path, data: dict[str, Any]) -> None:
    store, context_path, dashboard_path = memory_paths(root)
    atomic_write(store, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    atomic_write(context_path, render_context(data))
    try:
        from project_visualizer import render_dashboard
    except ImportError:
        visualizer_path = Path(__file__).with_name("project_visualizer.py")
        spec = importlib.util.spec_from_file_location("project_visualizer", visualizer_path)
        if not spec or not spec.loader: return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        render_dashboard = module.render_dashboard
    atomic_write(dashboard_path, render_dashboard(data))


def read_ignore_patterns(root: Path) -> list[str]:
    patterns: list[str] = []
    for name in (".gitignore", ".memoryignore"):
        path = root / name
        if not path.exists(): continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                patterns.append(line.rstrip("/"))
    return patterns


def ignored(relative: str, name: str, patterns: Iterable[str]) -> bool:
    if name in DEFAULT_IGNORES or relative in GENERATED_FILES: return True
    for pattern in patterns:
        clean = pattern.lstrip("/")
        if fnmatch.fnmatch(relative, clean) or fnmatch.fnmatch(name, clean): return True
        if relative == clean or relative.startswith(clean + "/"): return True
    return False


def detect_stack(files: list[dict[str, Any]]) -> list[str]:
    names = [Path(item["path"]).name for item in files]
    detected: list[str] = []
    for marker, label in STACK_MARKERS.items():
        if any(fnmatch.fnmatch(name, marker) for name in names) and label not in detected:
            detected.append(label)
    for label in (item.get("language") for item in files):
        if label in {"Python", "TypeScript", "JavaScript", "Java", "Kotlin", "C#", "Go", "Rust", "PHP", "Ruby", "Vue", "Svelte", "HTML", "CSS", "SQL"} and label not in detected:
            detected.append(label)
    return detected[:12]


def infer_modules(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = {}
    for item in files: buckets.setdefault(item.get("module", "root"), []).append(item["path"])
    return [{"name": name, "file_count": len(paths), "sample_files": paths[:8]} for name, paths in sorted(buckets.items(), key=lambda pair: (-len(pair[1]), pair[0]))][:50]


def infer_entrypoints(files: list[dict[str, Any]]) -> list[str]:
    return [item["path"] for item in files if Path(item["path"]).name in ENTRYPOINT_NAMES or Path(item["path"]).name.startswith("README")][:30]


def detect_agents(root: Path, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {str(item.get("key", "")).lower(): item for item in existing if isinstance(item, dict)}
    for key, marker in DETECTION_MARKERS.items():
        if (root / marker).exists():
            display_name, instruction_path = AGENT_ADAPTERS[key]
            current = by_key.get(key, {})
            by_key[key] = {"id": current.get("id", key), "key": key, "name": display_name, "instruction_file": instruction_path, "status": current.get("status", "detected"), "added_at": current.get("added_at", now_iso())}
    return sorted(by_key.values(), key=lambda item: item.get("name", ""))


def default_memory(root: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "project": {"name": root.name, "display_name": root.name.replace("_", " ").replace("-", " ").title(), "description": "", "root": ".", "created_at": now_iso(), "last_scanned": None},
        "summary": {}, "architecture": {"overview": "", "modules": []}, "entrypoints": [],
        "files": [], "graph": {"nodes": [], "edges": [], "summary": {}}, "history": [],
        "agents": [], "chats": [], "projects": [], "decisions": [], "tasks": [], "notes": [],
    }


def _changes(old: dict[str, Any], files: list[dict[str, Any]]) -> dict[str, list[str]]:
    old_signatures = {item.get("path"): item.get("signature") for item in old.get("files", []) if isinstance(item, dict)}
    new_signatures = {item["path"]: item["signature"] for item in files}
    return {
        "added": sorted(set(new_signatures) - set(old_signatures)),
        "changed": sorted(path for path in set(new_signatures) & set(old_signatures) if new_signatures[path] != old_signatures[path]),
        "removed": sorted(set(old_signatures) - set(new_signatures)),
    }


def _update_project_catalog(data: dict[str, Any], root: Path) -> None:
    projects = [item for item in data.get("projects", []) if Path(item.get("path", "")).resolve() != root]
    graph_summary = data.get("graph", {}).get("summary", {})
    projects.append({
        "id": re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-") or "project",
        "name": data["project"].get("display_name") or data["project"]["name"], "path": str(root),
        "description": data["project"].get("description", ""), "last_scanned": data["project"]["last_scanned"],
        "file_count": data["summary"].get("file_count", 0), "edge_count": graph_summary.get("edge_count", 0),
        "is_current": True,
    })
    data["projects"] = sorted(projects, key=lambda item: item.get("name", "").lower())


def scan(root: Path, description: str | None = None, max_files: int = 5000, display_name: str | None = None) -> dict[str, Any]:
    old = load_memory(root)
    data = default_memory(root)
    if old:
        for key in ("decisions", "tasks", "notes", "history", "agents", "chats", "projects"):
            if isinstance(old.get(key), list): data[key] = old[key]
        old_project = old.get("project", {})
        if isinstance(old_project, dict):
            for key in ("created_at", "description", "display_name"):
                if old_project.get(key) is not None: data["project"][key] = old_project[key]
        if isinstance(old.get("architecture"), dict): data["architecture"]["overview"] = old["architecture"].get("overview", "")
    if description is not None: data["project"]["description"] = description
    if display_name is not None: data["project"]["display_name"] = display_name

    files, truncated = scan_file_records(root, read_ignore_patterns(root), ignored, max_files)
    changes = _changes(old, files)
    graph = build_graph(root, files)
    scanned_at = now_iso()
    data["project"]["last_scanned"] = scanned_at
    data["project"]["tech_stack"] = detect_stack(files)
    data["files"], data["graph"] = files, graph
    data["entrypoints"] = infer_entrypoints(files)
    data["architecture"]["modules"] = infer_modules(files)
    data["agents"] = detect_agents(root, data["agents"])
    data["summary"] = {
        "file_count": len(files), "total_bytes": sum(item["size_bytes"] for item in files), "scan_truncated": truncated,
        "edge_count": graph["summary"]["edge_count"], "connected_files": graph["summary"]["connected_files"], "changes": changes,
    }
    if any(changes.values()) or not data["history"]:
        data["history"].append({"id": len(data["history"]) + 1, "scanned_at": scanned_at, **changes})
        data["history"] = data["history"][-HISTORY_LIMIT:]
    _update_project_catalog(data, root)
    save_memory(root, data)
    return data


def scan_snapshot(root: Path, display_name: str | None = None, max_files: int = 5000) -> dict[str, Any]:
    """Build a complete project snapshot without writing into that project."""
    old = load_memory(root)
    data = default_memory(root)
    if old:
        for key in ("decisions", "tasks", "notes", "history", "agents", "chats"):
            if isinstance(old.get(key), list): data[key] = old[key]
        old_project = old.get("project", {})
        if isinstance(old_project, dict):
            for key in ("created_at", "description", "display_name"):
                if old_project.get(key) is not None: data["project"][key] = old_project[key]
        if isinstance(old.get("architecture"), dict): data["architecture"]["overview"] = old["architecture"].get("overview", "")
    if display_name: data["project"]["display_name"] = display_name
    files, truncated = scan_file_records(root, read_ignore_patterns(root), ignored, max_files)
    changes = _changes(old, files)
    graph = build_graph(root, files)
    scanned_at = now_iso()
    data["project"]["root"] = str(root)
    data["project"]["last_scanned"] = scanned_at
    data["project"]["tech_stack"] = detect_stack(files)
    data["files"], data["graph"] = files, graph
    data["entrypoints"] = infer_entrypoints(files)
    data["architecture"]["modules"] = infer_modules(files)
    data["agents"] = detect_agents(root, data["agents"])
    data["summary"] = {"file_count": len(files), "total_bytes": sum(item["size_bytes"] for item in files), "scan_truncated": truncated, "edge_count": graph["summary"]["edge_count"], "connected_files": graph["summary"]["connected_files"], "changes": changes}
    if any(changes.values()) or not data["history"]:
        data["history"].append({"id": len(data["history"]) + 1, "scanned_at": scanned_at, **changes})
        data["history"] = data["history"][-HISTORY_LIMIT:]
    data["projects"] = []
    return data


def next_id(items: list[dict[str, Any]]) -> int:
    return max((int(item.get("id", 0)) for item in items if str(item.get("id", "")).isdigit()), default=0) + 1


def add_record(root: Path, collection: str, record: dict[str, Any]) -> dict[str, Any]:
    data = load_memory(root) or scan(root)
    items = data.setdefault(collection, [])
    record = {"id": next_id(items), **record, "created_at": record.get("created_at", now_iso())}
    items.append(record); save_memory(root, data); return record


def update_task(root: Path, task_id: int, status: str) -> dict[str, Any]:
    data = load_memory(root)
    for task in data.get("tasks", []):
        if int(task.get("id", -1)) == task_id:
            task["status"], task["updated_at"] = status, now_iso(); save_memory(root, data); return task
    raise SystemExit(f"Task {task_id} was not found")


def append_instruction(path: Path) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if "## Agent Memory" not in existing:
        atomic_write(path, existing.rstrip() + ("\n\n" if existing.strip() else "") + AGENT_INSTRUCTIONS)


def enable_agent(root: Path, key: str) -> dict[str, Any]:
    key = key.lower()
    if key not in AGENT_ADAPTERS: raise SystemExit(f"Unknown agent: {key}. Choose from: {', '.join(AGENT_ADAPTERS)}")
    name, instruction_file = AGENT_ADAPTERS[key]
    append_instruction(root / instruction_file)
    data = load_memory(root) or scan(root)
    agents = [item for item in data.get("agents", []) if item.get("key") != key]
    record = {"id": key, "key": key, "name": name, "instruction_file": instruction_file, "status": "enabled", "added_at": now_iso()}
    agents.append(record); data["agents"] = sorted(agents, key=lambda item: item["name"]); save_memory(root, data); return record


def register_agent(root: Path, name: str, instruction_file: str) -> dict[str, Any]:
    key = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "custom-agent"
    safe_path = Path(instruction_file)
    if safe_path.is_absolute() or ".." in safe_path.parts:
        raise SystemExit("Instruction file must be a path inside the project")
    append_instruction(root / safe_path)
    data = load_memory(root) or scan(root)
    agents = [item for item in data.get("agents", []) if item.get("key") != key]
    record = {"id": key, "key": key, "name": name, "instruction_file": safe_path.as_posix(), "status": "enabled", "added_at": now_iso()}
    agents.append(record); data["agents"] = sorted(agents, key=lambda item: item["name"]); save_memory(root, data); return record


def import_chat(root: Path, source: Path, agent: str, title: str, summary: str, created_at: str | None = None) -> dict[str, Any]:
    source = source.resolve()
    if not source.exists() or not source.is_file(): raise SystemExit(f"Chat source not found: {source}")
    try:
        with source.open("r", encoding="utf-8", errors="ignore") as handle:
            line_count = sum(1 for _ in handle)
    except OSError: line_count = 0
    stat = source.stat()
    return add_record(root, "chats", {"title": title, "agent": agent, "summary": summary, "source": str(source), "source_bytes": stat.st_size, "line_count": line_count, "created_at": created_at or datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"), "imported_at": now_iso()})


def track_project(root: Path, project_path: Path, description: str = "", display_name: str | None = None, source: str = "manual", source_id: str | None = None) -> dict[str, Any]:
    project_path = project_path.resolve()
    if not project_path.is_dir(): raise SystemExit(f"Project directory not found: {project_path}")
    target = load_memory(project_path)
    target_project, target_summary = target.get("project", {}), target.get("summary", {})
    if not target:
        target = default_memory(project_path)
        target["project"]["display_name"] = display_name or project_path.name
        target["project"]["description"] = description or "Agent Memory is not initialized in this project yet."
        target["summary"] = {"file_count": 0, "edge_count": 0, "connected_files": 0, "total_bytes": 0, "changes": {"added": [], "changed": [], "removed": []}}
        target_project, target_summary = target["project"], target["summary"]
    data = load_memory(root) or scan(root)
    projects = [item for item in data.get("projects", []) if Path(item.get("path", "")).resolve() != project_path]
    snapshot = {key: target.get(key) for key in ("schema_version", "project", "summary", "architecture", "entrypoints", "graph", "history", "agents", "chats", "decisions", "tasks", "notes")}
    record = {"id": re.sub(r"[^a-z0-9]+", "-", (source_id or project_path.name).lower()).strip("-") or f"project-{len(projects)+1}", "name": display_name or target_project.get("display_name") or target_project.get("name") or project_path.name, "path": str(project_path), "description": description or target_project.get("description", ""), "last_scanned": target_project.get("last_scanned"), "file_count": target_summary.get("file_count", 0), "edge_count": target_summary.get("edge_count", 0), "tracked_at": now_iso(), "source": source, "source_id": source_id, "is_current": project_path == root, "snapshot": snapshot}
    projects.append(record); data["projects"] = sorted(projects, key=lambda item: item["name"].lower()); save_memory(root, data); return record


def sync_projects(root: Path, manifest: Path, deep_scan: bool = False, max_files: int = 5000) -> list[dict[str, Any]]:
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read project manifest {manifest}: {exc}") from exc
    entries = payload.get("projects", payload if isinstance(payload, list) else [])
    if not isinstance(entries, list): raise SystemExit("Project manifest must contain a projects list")
    unique: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("path"): continue
        path = Path(entry["path"]).resolve()
        if not path.is_dir(): continue
        unique[os.path.normcase(str(path))] = entry
    if not deep_scan:
        return [track_project(root, Path(entry["path"]), display_name=entry.get("label"), source=entry.get("source", "manifest"), source_id=entry.get("projectId")) for entry in unique.values()]

    current = load_memory(root) or scan(root)
    transient: list[tuple[dict[str, Any], dict[str, Any]]] = []
    total_projects = len(unique)
    for project_index, entry in enumerate(unique.values(), start=1):
        project_path = Path(entry["path"]).resolve()
        print(f"[{project_index}/{total_projects}] Scanning {entry.get('label') or project_path.name}...", flush=True)
        snapshot = current if project_path == root else scan_snapshot(project_path, entry.get("label"), max_files)
        project = snapshot.get("project", {})
        summary = snapshot.get("summary", {})
        project_id = re.sub(r"[^a-z0-9-]+", "-", str(entry.get("projectId") or project_path.name).lower()).strip("-") or f"project-{len(transient)+1}"
        record = {"id": project_id, "name": entry.get("label") or project.get("display_name") or project_path.name, "path": str(project_path), "description": project.get("description", ""), "last_scanned": project.get("last_scanned"), "file_count": summary.get("file_count", 0), "edge_count": summary.get("edge_count", 0), "tracked_at": now_iso(), "source": entry.get("source", "manifest"), "source_id": entry.get("projectId"), "is_current": project_path == root}
        transient.append((record, snapshot))

    output_dir = root / ".agents" / "memory" / "projects"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        from project_visualizer import render_dashboard
    except ImportError:
        visualizer_path = Path(__file__).with_name("project_visualizer.py")
        spec = importlib.util.spec_from_file_location("project_visualizer", visualizer_path)
        if not spec or not spec.loader: raise SystemExit("Cannot load dashboard renderer")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); render_dashboard = module.render_dashboard

    catalog: list[dict[str, Any]] = []
    for record, _ in transient:
        item = dict(record)
        item["dashboard_file"] = "visualizer.html" if item["is_current"] else f"projects/{item['id']}.html"
        catalog.append(item)
    for record, snapshot in transient:
        if record["is_current"]: continue
        adjusted_catalog = []
        for item in catalog:
            adjusted = dict(item)
            adjusted["is_current"] = item["id"] == record["id"]
            adjusted["dashboard_file"] = "../visualizer.html" if item["is_current"] else f"{item['id']}.html"
            adjusted_catalog.append(adjusted)
        dashboard_data = {**snapshot, "projects": adjusted_catalog}
        atomic_write(output_dir / f"{record['id']}.json", json.dumps(dashboard_data, indent=2, ensure_ascii=False) + "\n")
        atomic_write(output_dir / f"{record['id']}.html", render_dashboard(dashboard_data))
    current["projects"] = sorted(catalog, key=lambda item: item["name"].lower())
    save_memory(root, current)
    return current["projects"]


def render_context(data: dict[str, Any]) -> str:
    project, architecture, graph = data.get("project", {}), data.get("architecture", {}), data.get("graph", {})
    name = project.get("display_name") or project.get("name", "Unknown")
    lines = [f"# Agent Memory: {name}", "", f"> Generated {project.get('last_scanned') or now_iso()}. Read this before exploring the repository.", ""]
    if project.get("description"): lines += [project["description"], ""]
    if architecture.get("overview"): lines += ["## Architecture", "", architecture["overview"], ""]
    if project.get("tech_stack"): lines += ["## Technology", "", ", ".join(project["tech_stack"]), ""]
    summary = graph.get("summary", {})
    lines += ["## Relationship Graph", "", f"{summary.get('node_count', 0)} file nodes, {summary.get('edge_count', 0)} resolved links, {summary.get('connected_files', 0)} connected files.", "", "Query a file's neighborhood without loading the full graph:", "", "`python .agents/memory/memory_manager.py related \"path/to/file\"`", ""]
    if data.get("entrypoints"): lines += ["## Start Here", ""] + [f"- `{item}`" for item in data["entrypoints"]] + [""]
    if architecture.get("modules"):
        lines += ["## Repository Map", ""]
        for module in architecture["modules"]:
            examples = ", ".join(f"`{path}`" for path in module.get("sample_files", [])[:3])
            lines.append(f"- **{module['name']}** — {module['file_count']} files" + (f"; e.g. {examples}" if examples else ""))
        lines.append("")
    if data.get("agents"): lines += ["## Available Agents", ""] + [f"- {item['name']} ({item.get('status', 'detected')}) — `{item.get('instruction_file', '')}`" for item in data["agents"]] + [""]
    collections = (("Active Tasks", [item for item in data.get("tasks", []) if item.get("status") not in {"done", "completed", "cancelled"}], lambda item: f"#{item['id']} [{item.get('status', 'pending')}] {item.get('title', '')}"), ("Decisions", data.get("decisions", []), lambda item: f"#{item['id']} {item.get('title', '')} — {item.get('rationale', '')}"), ("Notes", data.get("notes", []), lambda item: f"#{item['id']} {item.get('text', '')}"))
    for heading, items, formatter in collections:
        if items: lines += [f"## {heading}", ""] + [f"- {formatter(item)}" for item in items[-20:]] + [""]
    lines += ["## Agent Workflow", "", "1. Use this memory before recursively scanning files.", "2. Query `related` and inspect only source relevant to the task.", "3. Treat source as authoritative; memory may be stale.", "4. After meaningful changes, run `python .agents/memory/memory_manager.py scan`.", "5. Record durable decisions, tasks, and notes through the CLI.", ""]
    return "\n".join(lines)


def print_status(data: dict[str, Any]) -> None:
    project, summary = data.get("project", {}), data.get("summary", {})
    pending = sum(1 for task in data.get("tasks", []) if task.get("status", "pending") not in {"done", "completed", "cancelled"})
    print(f"Project: {project.get('display_name') or project.get('name', 'Unknown')}")
    print(f"Last scanned: {project.get('last_scanned', 'never')}")
    print(f"Files indexed: {summary.get('file_count', 0)}")
    print(f"Resolved links: {summary.get('edge_count', 0)}")
    print(f"Agents / chats / projects: {len(data.get('agents', []))} / {len(data.get('chats', []))} / {len(data.get('projects', []))}")
    print(f"Active tasks: {pending}; decisions: {len(data.get('decisions', []))}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent Memory: relationship-aware project memory for any AI coding agent")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: current directory)")
    sub = parser.add_subparsers(dest="command")
    scan_parser = sub.add_parser("scan", help="refresh repository memory and relationship graph"); scan_parser.add_argument("--description"); scan_parser.add_argument("--name", help="human-readable project name"); scan_parser.add_argument("--max-files", type=int, default=5000)
    sub.add_parser("context", help="print compact context for an agent"); sub.add_parser("status", help="show memory status")
    related = sub.add_parser("related", help="show files linked to a source file"); related.add_argument("path"); related.add_argument("--depth", type=int, default=1, choices=range(1, 4))
    task = sub.add_parser("add-task"); task.add_argument("title"); task.add_argument("category", nargs="?", default="General")
    update = sub.add_parser("update-task"); update.add_argument("id", type=int); update.add_argument("status", choices=["pending", "in-progress", "blocked", "done", "cancelled"])
    decision = sub.add_parser("log-decision"); decision.add_argument("title"); decision.add_argument("rationale")
    note = sub.add_parser("note"); note.add_argument("text")
    agent = sub.add_parser("enable-agent", help="add memory instructions for an AI agent"); agent.add_argument("agent", choices=sorted(AGENT_ADAPTERS))
    custom_agent = sub.add_parser("register-agent", help="connect any other agent using its project instruction file"); custom_agent.add_argument("name"); custom_agent.add_argument("--instructions", required=True, help="instruction file path inside the project")
    chat = sub.add_parser("import-chat", help="track chat metadata and an explicit summary without copying transcript text"); chat.add_argument("source", type=Path); chat.add_argument("--agent", required=True); chat.add_argument("--title", required=True); chat.add_argument("--summary", required=True); chat.add_argument("--date")
    project = sub.add_parser("track-project", help="add another project to this memory dashboard"); project.add_argument("path", type=Path); project.add_argument("--description", default="")
    sync = sub.add_parser("sync-projects", help="import and deduplicate projects from a JSON manifest"); sync.add_argument("manifest", type=Path); sync.add_argument("--scan", action="store_true", help="deep-scan every project and generate its dashboard"); sync.add_argument("--max-files", type=int, default=5000)
    serve = sub.add_parser("serve"); serve.add_argument("--port", type=int, default=28492)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv); root, command = args.root.resolve(), args.command or "scan"
    if command == "scan": print_status(scan(root, args.description, args.max_files, args.name))
    elif command == "context": print(render_context(load_memory(root) or scan(root)), end="")
    elif command == "status": print_status(load_memory(root) or scan(root))
    elif command == "related": print(json.dumps(related_files((load_memory(root) or scan(root)).get("graph", {}), args.path, args.depth), indent=2))
    elif command == "add-task":
        record = add_record(root, "tasks", {"title": args.title, "category": args.category, "status": "pending"}); print(f"Added task #{record['id']}: {record['title']}")
    elif command == "update-task":
        record = update_task(root, args.id, args.status); print(f"Task #{record['id']} is now {record['status']}")
    elif command == "log-decision":
        record = add_record(root, "decisions", {"title": args.title, "rationale": args.rationale}); print(f"Logged decision #{record['id']}: {record['title']}")
    elif command == "note":
        record = add_record(root, "notes", {"text": args.text}); print(f"Added note #{record['id']}")
    elif command == "enable-agent":
        record = enable_agent(root, args.agent); print(f"Enabled {record['name']} via {record['instruction_file']}")
    elif command == "register-agent":
        record = register_agent(root, args.name, args.instructions); print(f"Enabled {record['name']} via {record['instruction_file']}")
    elif command == "import-chat":
        record = import_chat(root, args.source, args.agent, args.title, args.summary, args.date); print(f"Imported chat metadata #{record['id']}: {record['title']}")
    elif command == "track-project":
        record = track_project(root, args.path, args.description); print(f"Tracking {record['name']}: {record['path']}")
    elif command == "sync-projects":
        records = sync_projects(root, args.manifest, args.scan, args.max_files); print(f"Synchronized {len(records)} unique projects" + (" with diagrams" if args.scan else ""))
    elif command == "serve":
        from server import run_server
        run_server(port=args.port)
    return 0


if __name__ == "__main__": raise SystemExit(main())
