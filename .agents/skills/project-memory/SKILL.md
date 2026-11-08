---
name: project-memory
description: Maintain relationship-aware Agent Memory for Codex, Antigravity, Gemini, Claude, Cursor, Copilot, Windsurf, Hermes, and other coding agents. Use it before broad exploration, to query linked files, and after meaningful project changes.
---

# Agent Memory

Use this skill to reuse repository structure, file relationships, decisions, tasks, chat summaries, and durable notes instead of rediscovering them in every chat. The store is project-local and never silently scans private chat history.

## Workflow

1. **Load memory first**: Read `.agents/memory/context.md`. If it is missing, run:
   ```bash
   python .agents/memory/memory_manager.py scan
   ```
2. **Query relationships** before exploring broadly:
   ```bash
   python .agents/memory/memory_manager.py related "path/to/file"
   ```
3. **Work narrowly**: Inspect the requested file and its relevant neighbors. Memory is a map, not proof that source code is unchanged.
4. **Refresh after meaningful changes** with the scan command above.
5. **Log durable architectural decisions**:
   ```bash
   python .agents/memory/memory_manager.py log-decision "Title" "Rationale"
   ```
6. **Track follow-up work**:
   ```bash
   python .agents/memory/memory_manager.py add-task "Task description" "Category"
    python .agents/memory/memory_manager.py update-task 1 done
   ```
7. **Record a durable fact** with `python .agents/memory/memory_manager.py note "Fact"`.
8. **View the dashboard**: Open `.agents/memory/visualizer.html`, or run `python .agents/memory/memory_manager.py serve`.

Never store secrets, credentials, personal chat transcripts, or generated build directories in project memory.
