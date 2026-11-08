# Agent Memory Instructions

Before broad repository exploration, read `.agents/memory/context.md`. Query `python .agents/memory/memory_manager.py related "path/to/file"` to locate connected files, then inspect only source relevant to the task. Always verify relevant source before editing.

After meaningful changes, run `python .agents/memory/memory_manager.py scan`.

Record durable architectural reasoning with `log-decision`, future work with `add-task`, and stable project facts with `note`. Chat tracking must be explicit and summary-only. Do not store secrets, credentials, source contents, or private conversation text in memory.
