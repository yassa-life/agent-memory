---
trigger: always_on
description: Memory-first project navigation for coding agents
---

# Project Memory Rule

- **Start compact**: Read `.agents/memory/context.md` before broad repository exploration.
- **Verify source**: Memory is a navigation aid. Read relevant source files before changing code.
- **Avoid redundant scans**: Do not recursively list the repository when the indexed map is current.
- **Rescan Command**: `python .agents/memory/memory_manager.py scan`
- **Durable knowledge**: Record architectural decisions, tasks, and notes through the memory CLI.
- **Privacy**: Never place secrets, credentials, or private chat transcripts in project memory.
