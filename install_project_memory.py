"""Install Project Memory into another repository."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent
MEMORY_FILES = ("memory_manager.py", "project_visualizer.py", "server.py", "memory_hook.py")
AGENT_TEXT = """\n\n## Project Memory\n\nBefore broad repository exploration, read `.agents/memory/context.md`. Verify relevant source before editing. After meaningful changes, run `python .agents/memory/memory_manager.py scan`. Record durable decisions with `log-decision` and follow-up work with `add-task`. Never store secrets or private chat history in memory.\n"""


def append_once(path: Path, text: str) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if "## Project Memory" not in existing:
        path.write_text(existing.rstrip() + text, encoding="utf-8")


def install(target: Path) -> None:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"Target is not a directory: {target}")
    memory_dir = target / ".agents" / "memory"
    skill_dir = target / ".agents" / "skills" / "project-memory"
    rules_dir = target / ".agents" / "rules"
    memory_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.mkdir(parents=True, exist_ok=True)
    rules_dir.mkdir(parents=True, exist_ok=True)
    for name in MEMORY_FILES:
        shutil.copy2(SOURCE_ROOT / ".agents" / "memory" / name, memory_dir / name)
    shutil.copy2(SOURCE_ROOT / ".agents" / "skills" / "project-memory" / "SKILL.md", skill_dir / "SKILL.md")
    shutil.copy2(SOURCE_ROOT / ".agents" / "rules" / "memory.md", rules_dir / "memory.md")
    hooks = target / ".agents" / "hooks.json"
    if not hooks.exists():
        shutil.copy2(SOURCE_ROOT / ".agents" / "hooks.json", hooks)
    append_once(target / "AGENTS.md", AGENT_TEXT)
    append_once(target / "GEMINI.md", AGENT_TEXT)
    subprocess.run([sys.executable, str(memory_dir / "memory_manager.py"), "--root", str(target), "scan"], check=True)
    print(f"Project Memory installed in {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Project Memory into a repository")
    parser.add_argument("target", type=Path)
    install(parser.parse_args().target)


if __name__ == "__main__":
    main()
