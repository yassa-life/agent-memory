---
name: project-memory
description: Maintain compact, project-local memory for Codex, Antigravity, Gemini, and other coding agents. Use it before broad repository exploration and after meaningful project changes.
---

# Portable Project Memory

Use this skill to reuse repository structure, decisions, tasks, and durable notes instead of rediscovering them in every chat. The store is project-local and does not scan private chat history.

## Workflow

1. **Load memory first**: Read `.agents/memory/context.md`. If it is missing, run:
   ```bash
   python .agents/memory/memory_manager.py scan
   ```
2. **Work narrowly**: Inspect only files relevant to the request. Memory is a map, not proof that source code is unchanged.
3. **Refresh after meaningful changes** with the scan command above.
4. **Log durable architectural decisions**:
   ```bash
   python .agents/memory/memory_manager.py log-decision "Title" "Rationale"
   ```
5. **Track follow-up work**:
   ```bash
   python .agents/memory/memory_manager.py add-task "Task description" "Category"
    python .agents/memory/memory_manager.py update-task 1 done
   ```
6. **Record a durable fact** with `python .agents/memory/memory_manager.py note "Fact"`.
7. **View the dashboard**: Open `.agents/memory/visualizer.html`, or run `python .agents/memory/memory_manager.py serve`.

Never store secrets, credentials, personal chat transcripts, or generated build directories in project memory.
