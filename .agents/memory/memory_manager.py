"""Portable, zero-dependency project memory for AI coding agents."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.util
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 2
DEFAULT_IGNORES = {".git", ".hg", ".svn", ".idea", ".vscode", ".venv", "venv", "node_modules", "dist", "build", "coverage", "__pycache__", ".pytest_cache", ".mypy_cache", ".next", ".nuxt", "target", "vendor"}
GENERATED_FILES = {".agents/memory/memory.json", ".agents/memory/context.md", ".agents/memory/visualizer.html"}
STACK_MARKERS = {"package.json": "Node.js / JavaScript", "pyproject.toml": "Python", "requirements.txt": "Python", "pom.xml": "Java / Maven", "build.gradle": "Java / Gradle", "build.gradle.kts": "Kotlin / Gradle", "Cargo.toml": "Rust", "go.mod": "Go", "composer.json": "PHP", "Gemfile": "Ruby", "pubspec.yaml": "Dart / Flutter", "*.sln": ".NET", "*.csproj": ".NET"}
ENTRYPOINT_NAMES = {"main.py", "app.py", "server.py", "manage.py", "index.js", "index.ts", "main.js", "main.ts", "main.tsx", "App.tsx", "Program.cs", "Main.java", "Dockerfile", "docker-compose.yml", "docker-compose.yaml"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def normalize(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def memory_paths(root: Path) -> tuple[Path, Path, Path]:
    directory = root / ".agents" / "memory"
    return directory / "memory.json", directory / "context.md", directory / "visualizer.html"


def load_memory(root: Path) -> dict[str, Any]:
    store, _, _ = memory_paths(root)
    if not store.exists():
        return {}
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
        if not spec or not spec.loader:
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        render_dashboard = module.render_dashboard
    atomic_write(dashboard_path, render_dashboard(data))


def read_ignore_patterns(root: Path) -> list[str]:
    patterns: list[str] = []
    for name in (".gitignore", ".memoryignore"):
        path = root / name
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                patterns.append(line.rstrip("/"))
    return patterns


def ignored(relative: str, name: str, patterns: Iterable[str]) -> bool:
    if name in DEFAULT_IGNORES or relative in GENERATED_FILES:
        return True
    for pattern in patterns:
        clean = pattern.lstrip("/")
        if fnmatch.fnmatch(relative, clean) or fnmatch.fnmatch(name, clean):
            return True
        if relative == clean or relative.startswith(clean + "/"):
            return True
    return False


def file_signature(path: Path) -> str:
    stat = path.stat()
    return hashlib.sha1(f"{stat.st_size}:{stat.st_mtime_ns}".encode()).hexdigest()[:12]


def scan_files(root: Path, max_files: int = 5000) -> tuple[list[dict[str, Any]], bool]:
    patterns = read_ignore_patterns(root)
    files: list[dict[str, Any]] = []
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        rel_dir = "" if current_path == root else normalize(current_path, root)
        dirnames[:] = sorted(d for d in dirnames if not ignored(f"{rel_dir}/{d}".strip("/"), d, patterns))
        for filename in sorted(filenames):
            path = current_path / filename
            relative = normalize(path, root)
            if ignored(relative, filename, patterns):
                continue
            try:
                stat = path.stat()
                files.append({"path": relative, "size_bytes": stat.st_size, "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"), "signature": file_signature(path)})
            except OSError:
                continue
            if len(files) >= max_files:
                return files, True
    return files, False


def detect_stack(files: list[dict[str, Any]]) -> list[str]:
    names = [Path(item["path"]).name for item in files]
    detected: list[str] = []
    for marker, label in STACK_MARKERS.items():
        if any(fnmatch.fnmatch(name, marker) for name in names) and label not in detected:
            detected.append(label)
    extensions = {Path(item["path"]).suffix.lower() for item in files}
    for extension, label in {".py": "Python", ".tsx": "TypeScript / React", ".ts": "TypeScript", ".jsx": "JavaScript / React", ".vue": "Vue", ".svelte": "Svelte", ".html": "HTML", ".css": "CSS", ".sql": "SQL"}.items():
        if extension in extensions and label not in detected:
            detected.append(label)
    return detected[:12]


def infer_modules(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = {}
    for item in files:
        parts = Path(item["path"]).parts
        buckets.setdefault(parts[0] if len(parts) > 1 else "root", []).append(item["path"])
    return [{"name": name, "file_count": len(paths), "sample_files": paths[:8]} for name, paths in sorted(buckets.items(), key=lambda pair: (-len(pair[1]), pair[0]))][:30]


def infer_entrypoints(files: list[dict[str, Any]]) -> list[str]:
    return [item["path"] for item in files if Path(item["path"]).name in ENTRYPOINT_NAMES or Path(item["path"]).name.startswith("README")][:30]


def default_memory(root: Path) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "project": {"name": root.name, "description": "", "root": ".", "created_at": now_iso(), "last_scanned": None}, "summary": {}, "architecture": {"overview": "", "modules": []}, "entrypoints": [], "files": [], "decisions": [], "tasks": [], "notes": []}


def scan(root: Path, description: str | None = None, max_files: int = 5000) -> dict[str, Any]:
    old = load_memory(root)
    data = default_memory(root)
    if old:
        for key in ("decisions", "tasks", "notes"):
            if isinstance(old.get(key), list):
                data[key] = old[key]
        old_project = old.get("project", {})
        if isinstance(old_project, dict):
            data["project"]["created_at"] = old_project.get("created_at", data["project"]["created_at"])
            data["project"]["description"] = old_project.get("description", "")
        old_architecture = old.get("architecture", {})
        if isinstance(old_architecture, dict):
            data["architecture"]["overview"] = old_architecture.get("overview", "")
    if description is not None:
        data["project"]["description"] = description
    files, truncated = scan_files(root, max_files=max_files)
    old_signatures = {item.get("path"): item.get("signature") for item in old.get("files", []) if isinstance(item, dict)}
    new_signatures = {item["path"]: item["signature"] for item in files}
    added = sorted(set(new_signatures) - set(old_signatures))
    removed = sorted(set(old_signatures) - set(new_signatures))
    changed = sorted(path for path in set(new_signatures) & set(old_signatures) if new_signatures[path] != old_signatures[path])
    data["project"]["last_scanned"] = now_iso()
    data["project"]["tech_stack"] = detect_stack(files)
    data["files"] = files
    data["entrypoints"] = infer_entrypoints(files)
    data["architecture"]["modules"] = infer_modules(files)
    data["summary"] = {"file_count": len(files), "total_bytes": sum(item["size_bytes"] for item in files), "scan_truncated": truncated, "changes": {"added": added[:100], "changed": changed[:100], "removed": removed[:100]}}
    save_memory(root, data)
    return data


def next_id(items: list[dict[str, Any]]) -> int:
    return max((int(item.get("id", 0)) for item in items), default=0) + 1


def add_record(root: Path, collection: str, record: dict[str, Any]) -> dict[str, Any]:
    data = load_memory(root) or scan(root)
    items = data.setdefault(collection, [])
    record = {"id": next_id(items), **record, "created_at": now_iso()}
    items.append(record)
    save_memory(root, data)
    return record


def update_task(root: Path, task_id: int, status: str) -> dict[str, Any]:
    data = load_memory(root)
    for task in data.get("tasks", []):
        if int(task.get("id", -1)) == task_id:
            task["status"] = status
            task["updated_at"] = now_iso()
            save_memory(root, data)
            return task
    raise SystemExit(f"Task {task_id} was not found")


def render_context(data: dict[str, Any]) -> str:
    project, architecture = data.get("project", {}), data.get("architecture", {})
    lines = [f"# Project Memory: {project.get('name', 'Unknown')}", "", f"> Generated {project.get('last_scanned') or now_iso()}. Read this before exploring the repository.", ""]
    if project.get("description"):
        lines += [project["description"], ""]
    if architecture.get("overview"):
        lines += ["## Architecture", "", architecture["overview"], ""]
    if project.get("tech_stack"):
        lines += ["## Technology", "", ", ".join(project["tech_stack"]), ""]
    if data.get("entrypoints"):
        lines += ["## Start Here", ""] + [f"- `{item}`" for item in data["entrypoints"]] + [""]
    if architecture.get("modules"):
        lines += ["## Repository Map", ""]
        for module in architecture["modules"]:
            examples = ", ".join(f"`{p}`" for p in module.get("sample_files", [])[:3])
            lines.append(f"- **{module['name']}** — {module['file_count']} files" + (f"; e.g. {examples}" if examples else ""))
        lines.append("")
    collections = (("Active Tasks", [x for x in data.get("tasks", []) if x.get("status") not in {"done", "completed", "cancelled"}], lambda x: f"#{x['id']} [{x.get('status', 'pending')}] {x.get('title', '')}"), ("Decisions", data.get("decisions", []), lambda x: f"#{x['id']} {x.get('title', '')} — {x.get('rationale', '')}"), ("Notes", data.get("notes", []), lambda x: f"#{x['id']} {x.get('text', '')}"))
    for heading, items, formatter in collections:
        if items:
            lines += [f"## {heading}", ""] + [f"- {formatter(item)}" for item in items[-20:]] + [""]
    lines += ["## Agent Workflow", "", "1. Use this memory before recursively scanning files.", "2. Inspect only files relevant to the current task.", "3. After meaningful changes, run `python .agents/memory/memory_manager.py scan`.", "4. Record durable reasoning with `log-decision`; track follow-up work with `add-task`.", ""]
    return "\n".join(lines)


def print_status(data: dict[str, Any]) -> None:
    project, summary = data.get("project", {}), data.get("summary", {})
    pending = sum(1 for task in data.get("tasks", []) if task.get("status", "pending") not in {"done", "completed", "cancelled"})
    print(f"Project: {project.get('name', 'Unknown')}")
    print(f"Last scanned: {project.get('last_scanned', 'never')}")
    print(f"Files indexed: {summary.get('file_count', 0)}")
    print(f"Active tasks: {pending}")
    print(f"Decisions: {len(data.get('decisions', []))}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Portable project memory for AI coding agents")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: current directory)")
    sub = parser.add_subparsers(dest="command")
    scan_parser = sub.add_parser("scan", help="refresh repository memory")
    scan_parser.add_argument("--description", help="set or replace the project description")
    scan_parser.add_argument("--max-files", type=int, default=5000)
    sub.add_parser("context", help="print compact context for an agent")
    sub.add_parser("status", help="show memory status")
    task = sub.add_parser("add-task", help="add a task"); task.add_argument("title"); task.add_argument("category", nargs="?", default="General")
    update = sub.add_parser("update-task", help="change a task status"); update.add_argument("id", type=int); update.add_argument("status", choices=["pending", "in-progress", "blocked", "done", "cancelled"])
    decision = sub.add_parser("log-decision", help="record an architectural decision"); decision.add_argument("title"); decision.add_argument("rationale")
    note = sub.add_parser("note", help="record a durable project note"); note.add_argument("text")
    serve = sub.add_parser("serve", help="open the local memory dashboard server"); serve.add_argument("--port", type=int, default=28492)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root, command = args.root.resolve(), args.command or "scan"
    if command == "scan":
        print_status(scan(root, args.description, args.max_files))
    elif command == "context":
        print(render_context(load_memory(root) or scan(root)), end="")
    elif command == "status":
        print_status(load_memory(root) or scan(root))
    elif command == "add-task":
        record = add_record(root, "tasks", {"title": args.title, "category": args.category, "status": "pending"}); print(f"Added task #{record['id']}: {record['title']}")
    elif command == "update-task":
        record = update_task(root, args.id, args.status); print(f"Task #{record['id']} is now {record['status']}")
    elif command == "log-decision":
        record = add_record(root, "decisions", {"title": args.title, "rationale": args.rationale}); print(f"Logged decision #{record['id']}: {record['title']}")
    elif command == "note":
        record = add_record(root, "notes", {"text": args.text}); print(f"Added note #{record['id']}")
    elif command == "serve":
        from server import run_server
        run_server(port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
