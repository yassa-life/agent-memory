# Project Memory: Antigravity_memeory

> Generated 2026-11-08T11:39:53+05:30. Read this before exploring the repository.

Portable project memory for AI coding agents. It indexes repository structure, preserves decisions and tasks, and generates compact context so agents avoid repeated full-project exploration.

## Architecture

A dependency-free Python memory engine indexes project metadata, preserves human-approved tasks and decisions, generates compact Markdown context for agents, and produces an offline HTML dashboard. Agent instruction files integrate the same workflow with Codex and Antigravity/Gemini.

## Technology

Python

## Start Here

- `README.md`
- `.agents/memory/server.py`

## Repository Map

- **.agents** — 7 files; e.g. `.agents/hooks.json`, `.agents/memory/memory_hook.py`, `.agents/memory/memory_manager.py`
- **root** — 5 files; e.g. `.gitignore`, `AGENTS.md`, `GEMINI.md`
- **tests** — 1 files; e.g. `tests/test_memory_manager.py`

## Decisions

- #1 Adopt Visual Antigravity Memory System — Avoid spending unnecessary context tokens repeatedly scanning the filesystem by reading memory.json first.
- #2 Use project-local, agent-neutral memory — Portable metadata and explicit durable notes work across Codex, Antigravity, Gemini, and other agents without collecting private chat history.

## Agent Workflow

1. Use this memory before recursively scanning files.
2. Inspect only files relevant to the current task.
3. After meaningful changes, run `python .agents/memory/memory_manager.py scan`.
4. Record durable reasoning with `log-decision`; track follow-up work with `add-task`.
