# Agent Instructions

Before broad repository exploration, read `.agents/memory/context.md`. Use its repository map to inspect only files relevant to the current task. Always verify relevant source before editing.

After meaningful changes, run `python .agents/memory/memory_manager.py scan`.

Record durable architectural reasoning with `log-decision`, future work with `add-task`, and stable project facts with `note`. Do not store secrets, credentials, or private conversation history in memory.
