# Project Memory for AI Agents

Project Memory gives Codex, Antigravity, Gemini, and other coding agents a small, durable map of a repository. It prevents every new chat from spending time and context tokens rediscovering the same structure, decisions, and unfinished work.

It is local-first, dependency-free, and privacy-conscious. The normal scan reads file metadata and paths only; it does not upload code or read private agent chat history.

## What it creates

- `.agents/memory/memory.json` — structured source of truth for tools.
- `.agents/memory/context.md` — compact context intended for agents to read first.
- `.agents/memory/visualizer.html` — self-contained human dashboard.
- `.agents/skills/project-memory/SKILL.md` — reusable skill instructions.
- `AGENTS.md` and `GEMINI.md` — automatic guidance for Codex and Antigravity/Gemini.

## Use it in this project

```text
python .agents/memory/memory_manager.py scan
python .agents/memory/memory_manager.py context
python .agents/memory/memory_manager.py status
```

Keep durable knowledge:

```text
python .agents/memory/memory_manager.py log-decision "Use PostgreSQL" "Transactions and relational reporting are required"
python .agents/memory/memory_manager.py add-task "Add migration rollback test" "Database"
python .agents/memory/memory_manager.py update-task 1 done
python .agents/memory/memory_manager.py note "Production deploys from the main branch"
```

Run the local dashboard:

```text
python .agents/memory/memory_manager.py serve
```

Then open `http://localhost:28492`. The server binds only to the local computer.

## Install it into another project

From this repository, run:

```text
python install_project_memory.py D:\path\to\another-project
```

The installer copies the engine, skill, and Antigravity rule; adds small memory-first sections to `AGENTS.md` and `GEMINI.md` without replacing existing instructions; and performs the first scan. It installs the supplied Antigravity hooks only when the target has no existing `hooks.json`, so it never overwrites another hook setup.

## Agent workflow

1. Read `.agents/memory/context.md` before broad exploration.
2. Use the map to open only relevant source files.
3. Treat source files as authoritative; memory may be stale.
4. Refresh after meaningful file changes.
5. Record reasoning that a future chat should not have to reconstruct.

Add repository-specific exclusions to `.memoryignore` using the same common patterns as `.gitignore`. Generated memory files, dependencies, build output, caches, and VCS directories are excluded automatically.

## Privacy and scope

Project Memory stores paths, sizes, timestamps, derived project structure, and facts explicitly added through its CLI. Do not put secrets or credentials into decisions or notes. Global chat-history analytics from the original prototype are not part of the product path.

## Requirements

Python 3.10 or later. No third-party packages are required.
