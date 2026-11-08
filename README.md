# Agent Memory

Agent Memory is a local-first memory and relationship layer for AI coding agents. It works with Codex, Antigravity, Gemini, Claude, Cursor, GitHub Copilot, Windsurf, Hermes, and generic agents instead of belonging to one model or vendor.

Every project file becomes a node. Project-local imports, includes, assets, and document links become edges. Agents can query a file's immediate neighborhood instead of recursively exploring the repository and spending context tokens on unrelated code.

## Why it reduces token usage

Traditional coding-agent sessions repeatedly rediscover the same repository structure. Agent Memory creates two efficient access paths:

- `.agents/memory/context.md` gives a compact project map, entrypoints, decisions, tasks, and graph statistics.
- `related <file>` returns only the files connected to the current source file.

The source code remains authoritative. Memory tells the agent where to look; it does not replace reading the relevant implementation.

## Core capabilities

### File relationship graph

- One node per indexed file.
- Edges for Python imports, JavaScript/TypeScript imports and requires, Java/Kotlin imports, C/C++ includes, HTML assets, CSS imports, and Markdown links.
- Content hashes detect real edits without storing source text.
- Interactive offline SVG visualization with search and file details.
- Focused relationship queries up to three levels deep.

### Any-agent integration

Enable memory instructions for a supported agent:

```text
python .agents/memory/memory_manager.py enable-agent codex
python .agents/memory/memory_manager.py enable-agent antigravity
python .agents/memory/memory_manager.py enable-agent gemini
python .agents/memory/memory_manager.py enable-agent claude
python .agents/memory/memory_manager.py enable-agent cursor
python .agents/memory/memory_manager.py enable-agent copilot
python .agents/memory/memory_manager.py enable-agent windsurf
python .agents/memory/memory_manager.py enable-agent hermes
```

The command creates or safely appends to that agent's normal instruction file. Existing instructions are preserved.

Connect an agent that is not in the built-in list:

```text
python .agents/memory/memory_manager.py register-agent "My Agent" --instructions ".my-agent/instructions.md"
```

### Dated edit history

Each meaningful scan records added, changed, and removed files with a timestamp. The dashboard can filter scan history by date.

### Project and chat catalogue

Track another initialized project:

```text
python .agents/memory/memory_manager.py track-project D:\path\to\project
```

The command embeds a metadata-only snapshot in the current dashboard. Use the **Project** selector below the dashboard metrics to switch its graph, history, tasks, decisions, agents, and chats. Re-run `track-project` when the other project's memory changes.

Synchronize many projects from a local integration manifest, such as a Codex project export:

```text
python .agents/memory/memory_manager.py sync-projects .agents/memory/codex_projects.local.json
```

Duplicate paths are removed automatically. Projects that have not initialized Agent Memory still appear in the selector with an empty-state snapshot. Local manifests and generated dashboards are Git-ignored because they contain machine-specific paths.

Import chat metadata with an explicit summary:

```text
python .agents/memory/memory_manager.py import-chat chat.jsonl --agent Claude --title "Architecture discussion" --summary "Selected the service boundary"
```

Transcript text is not copied into memory or the dashboard. Agent Memory stores the title, agent, explicit summary, source path, size, line count, and dates. It never silently scans private chat folders.

Use the dashboard's **AI agent** selector to change the active agent context and filter chats for that agent.

## Install into a project

From this repository:

```text
python install_project_memory.py D:\path\to\project
```

The installer copies the engine, relationship graph builder, dashboard, skill, rule, and safe default instructions. It performs the first scan without replacing an existing hook configuration.

## Everyday commands

Create or refresh memory:

```text
python .agents/memory/memory_manager.py scan --name "My Project" --description "What this project does"
```

Load compact context:

```text
python .agents/memory/memory_manager.py context
```

Ask what is connected to a file:

```text
python .agents/memory/memory_manager.py related "src/services/auth.ts"
python .agents/memory/memory_manager.py related "src/services/auth.ts" --depth 2
```

Keep durable project knowledge:

```text
python .agents/memory/memory_manager.py log-decision "Use PostgreSQL" "Relational reporting and transactions are required"
python .agents/memory/memory_manager.py add-task "Add rollback test" "Database"
python .agents/memory/memory_manager.py update-task 1 done
python .agents/memory/memory_manager.py note "Production deploys from main"
```

View status or run the dashboard:

```text
python .agents/memory/memory_manager.py status
python .agents/memory/memory_manager.py serve
```

Open `http://localhost:28492` after starting the server. It binds only to the local computer. The generated dashboard also works directly from `.agents/memory/visualizer.html`.

## Generated memory

- `.agents/memory/memory.json` — schema v3 data store with nodes, edges, history, agents, projects, chats, tasks, decisions, and notes.
- `.agents/memory/context.md` — compact agent-first context.
- `.agents/memory/visualizer.html` — self-contained visual dashboard.

## Privacy

Agent Memory stores file paths, metadata, content hashes, resolved relationships, and information explicitly added through commands. It does not store file contents. It does not upload data. It does not automatically collect conversations. Do not place secrets or credentials in notes, decisions, task names, or chat summaries.

Add project-specific exclusions to `.memoryignore` using common `.gitignore`-style patterns. Dependencies, build output, caches, VCS directories, and generated memory artifacts are excluded automatically.

## Requirements

Python 3.10 or later. No third-party packages, hosted database, JavaScript framework, or CDN is required.
