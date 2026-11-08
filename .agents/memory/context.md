# Agent Memory: Agent Memory

> Generated 2026-11-08T12:17:50+05:30. Read this before exploring the repository.

Relationship-aware, local-first memory for any AI coding agent. It maps files as connected nodes, tracks dated changes, and carries project context across models without storing source or transcript text.

## Architecture

A dependency-free Python memory engine indexes project metadata, preserves human-approved tasks and decisions, generates compact Markdown context for agents, and produces an offline HTML dashboard. Agent instruction files integrate the same workflow with Codex and Antigravity/Gemini.

## Technology

Python

## Relationship Graph

14 file nodes, 4 resolved links, 5 connected files.

Query a file's neighborhood without loading the full graph:

`python .agents/memory/memory_manager.py related "path/to/file"`

## Start Here

- `README.md`
- `.agents/memory/server.py`

## Repository Map

- **.agents** — 8 files; e.g. `.agents/hooks.json`, `.agents/memory/memory_hook.py`, `.agents/memory/memory_manager.py`
- **root** — 5 files; e.g. `.gitignore`, `AGENTS.md`, `GEMINI.md`
- **tests** — 1 files; e.g. `tests/test_memory_manager.py`

## Available Agents

- Antigravity (detected) — `GEMINI.md`
- Codex (detected) — `AGENTS.md`
- Gemini (detected) — `GEMINI.md`

## Decisions

- #1 Adopt Visual Antigravity Memory System — Avoid spending unnecessary context tokens repeatedly scanning the filesystem by reading memory.json first.
- #2 Use project-local, agent-neutral memory — Portable metadata and explicit durable notes work across Codex, Antigravity, Gemini, and other agents without collecting private chat history.
- #3 Use a resolved file relationship graph — Agents can query relevant neighboring files without loading the full repository or relying on opaque embeddings.
- #4 Keep chat tracking explicit and summary-only — The product tracks useful conversation context without silently collecting or embedding private transcript text.

## Agent Workflow

1. Use this memory before recursively scanning files.
2. Query `related` and inspect only source relevant to the task.
3. Treat source as authoritative; memory may be stale.
4. After meaningful changes, run `python .agents/memory/memory_manager.py scan`.
5. Record durable decisions, tasks, and notes through the CLI.
