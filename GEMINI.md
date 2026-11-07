# Project Memory Protocol

At the start of a task, read `.agents/memory/context.md`. Use it to locate relevant files without repeatedly scanning the full repository. Verify relevant source before editing because memory is a map, not a substitute for source code.

After meaningful changes, run `python .agents/memory/memory_manager.py scan`.

Record durable decisions and unfinished tasks with the CLI. Never store secrets or private chat transcripts in project memory. The visual dashboard is `.agents/memory/visualizer.html`.
