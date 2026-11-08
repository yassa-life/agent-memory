---
trigger: always_on
description: Memory-first project navigation for coding agents
---

# Agent Memory Rule

- **Start compact**: Read `.agents/memory/context.md` before broad repository exploration.
- **Follow relationships**: Use `python .agents/memory/memory_manager.py related "path/to/file"` before recursively searching for dependencies.
- **Verify source**: Memory is a navigation aid. Read relevant source files before changing code.
- **Avoid redundant scans**: Do not recursively list the repository when the indexed map is current.
- **Rescan Command**: `python .agents/memory/memory_manager.py scan`
- **Durable knowledge**: Record architectural decisions, tasks, and notes through the memory CLI.
- **Privacy**: Never place secrets, credentials, source contents, or private chat transcripts in Agent Memory. Chat imports store explicit summaries and metadata only.
