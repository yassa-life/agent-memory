"""Generate the self-contained Project Memory dashboard."""

from __future__ import annotations

import html
import json
from typing import Any


def render_dashboard(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    project = data.get("project", {})
    name = html.escape(project.get("display_name") or project.get("name", "Agent Memory"))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{name} / Agent Memory</title>
<style>
:root {{
  --paper: #f2f5f6;
  --surface: #ffffff;
  --ink: #101820;
  --muted: #65737d;
  --rule: #ccd5da;
  --soft-rule: #e5eaed;
  --cobalt: #2556d8;
  --cobalt-soft: #e8edfc;
  --signal: #f06a3a;
  --success: #176b55;
  --content: 1420px;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Aptos", "Segoe UI", Arial, sans-serif;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}
button, input {{ font: inherit; }}
a {{ color: inherit; }}
.shell {{ max-width: var(--content); margin: 0 auto; padding: 0 32px 72px; }}
.topline {{ height: 10px; background: var(--cobalt); }}
.masthead {{
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr) 260px;
  gap: 32px;
  align-items: end;
  min-height: 248px;
  padding: 48px 0 34px;
  border-bottom: 1px solid var(--ink);
}}
.mark {{
  width: 72px;
  height: 72px;
  display: grid;
  place-items: center;
  background: var(--ink);
  color: white;
  font-size: 21px;
  font-weight: 750;
  letter-spacing: -.04em;
  position: relative;
}}
.mark::after {{
  content: "";
  position: absolute;
  right: -9px;
  bottom: -9px;
  width: 18px;
  height: 18px;
  background: var(--signal);
}}
.project-name {{
  margin: 0;
  max-width: 960px;
  font-size: clamp(48px, 6vw, 86px);
  font-weight: 680;
  line-height: .91;
  letter-spacing: -.065em;
  overflow-wrap: break-word;
}}
.project-description {{
  max-width: 64ch;
  margin: 24px 0 0;
  color: #3f4d56;
  font-size: 17px;
  line-height: 1.55;
}}
.snapshot {{ align-self: stretch; display: flex; flex-direction: column; justify-content: space-between; }}
.snapshot-state {{ display: flex; align-items: center; gap: 9px; font-weight: 650; }}
.pulse {{ width: 9px; height: 9px; border-radius: 50%; background: var(--success); }}
.snapshot-time {{ color: var(--muted); font-size: 13px; max-width: 28ch; }}
.metrics {{
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  border-bottom: 1px solid var(--ink);
}}
.metric {{ padding: 22px 16px 20px 0; min-height: 122px; }}
.metric + .metric {{ border-left: 1px solid var(--rule); padding-left: 24px; }}
.metric-value {{ font-size: clamp(30px, 3.2vw, 48px); font-weight: 650; line-height: 1; letter-spacing: -.045em; }}
.metric-label {{ margin-top: 10px; color: var(--muted); font-size: 13px; }}
.context-rail {{ display: grid; grid-template-columns: minmax(220px, .8fr) minmax(220px, .8fr) minmax(300px, 1.4fr); border-bottom: 1px solid var(--ink); background: var(--surface); }}
.context-control {{ padding: 18px 22px 19px 0; }}
.context-control + .context-control, .agent-context {{ border-left: 1px solid var(--rule); padding-left: 22px; }}
.context-control label {{ display: block; color: var(--muted); font-size: 12px; margin-bottom: 7px; }}
.context-control select {{ width: 100%; border: 0; border-bottom: 1px solid var(--ink); border-radius: 0; background: transparent; color: var(--ink); padding: 5px 26px 7px 0; font-weight: 650; outline: none; }}
.context-control select:focus {{ border-bottom: 3px solid var(--cobalt); padding-bottom: 5px; }}
.agent-context {{ padding-top: 18px; padding-bottom: 18px; align-self: stretch; }}
.agent-context strong {{ display: block; }}
.agent-context span {{ display: block; color: var(--muted); font-size: 12px; margin-top: 4px; overflow-wrap: anywhere; }}
.workspace {{ display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 64px; padding-top: 48px; }}
.index {{ align-self: start; position: sticky; top: 28px; }}
.index-block {{ padding: 0 0 28px; margin-bottom: 28px; border-bottom: 1px solid var(--rule); }}
.section-title {{ margin: 0 0 17px; font-size: 14px; font-weight: 720; letter-spacing: -.01em; }}
.stack-list {{ display: flex; flex-wrap: wrap; gap: 7px; }}
.stack-item {{ padding: 5px 9px; border: 1px solid var(--rule); background: var(--surface); font-size: 12px; }}
.path-list, .jump-list {{ list-style: none; margin: 0; padding: 0; }}
.path-list li {{ margin-top: 10px; }}
code {{ font-family: "Cascadia Code", Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
.path-list code {{ color: var(--cobalt); }}
.jump-list a {{ display: block; padding: 7px 0; color: var(--muted); text-decoration: none; border-bottom: 1px solid transparent; }}
.jump-list a:hover, .jump-list a:focus-visible {{ color: var(--ink); border-color: var(--ink); outline: none; }}
.main-column {{ min-width: 0; }}
.section {{ padding-bottom: 62px; margin-bottom: 54px; border-bottom: 1px solid var(--ink); }}
.section:last-child {{ margin-bottom: 0; }}
.section-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 24px; margin-bottom: 25px; }}
.section-head h2 {{ margin: 0; font-size: 28px; font-weight: 650; letter-spacing: -.035em; }}
.section-meta {{ color: var(--muted); font-size: 13px; white-space: nowrap; }}
.search {{ position: relative; width: min(360px, 100%); }}
.search input {{
  width: 100%;
  border: 0;
  border-bottom: 1px solid var(--ink);
  border-radius: 0;
  background: transparent;
  color: var(--ink);
  padding: 8px 30px 8px 0;
  outline: none;
}}
.search input:focus {{ border-bottom-width: 3px; padding-bottom: 6px; }}
.search span {{ position: absolute; right: 0; bottom: 8px; color: var(--muted); pointer-events: none; }}
.graph-shell {{ background: var(--ink); color: white; border-top: 6px solid var(--cobalt); }}
.graph-toolbar {{ display: flex; justify-content: space-between; align-items: center; gap: 20px; padding: 18px 20px; border-bottom: 1px solid #34414b; }}
.graph-toolbar .search input {{ color: white; border-color: #74818a; }}
.graph-toolbar .search input::placeholder {{ color: #9da8af; }}
.graph-legend {{ color: #aab4ba; font-size: 12px; }}
.graph-stage {{ width: 100%; min-height: 520px; display: block; overflow: hidden; }}
.graph-stage svg {{ display: block; width: 100%; height: 520px; }}
.graph-edge {{ stroke: #53616b; stroke-width: 1; opacity: .62; vector-effect: non-scaling-stroke; }}
.graph-node circle {{ fill: #f2f5f6; stroke: var(--ink); stroke-width: 1.5; cursor: pointer; vector-effect: non-scaling-stroke; }}
.graph-node.is-connected circle {{ fill: #8fa9ff; }}
.graph-node.is-hub circle {{ fill: var(--signal); }}
.graph-node text {{ fill: #dbe3e7; font: 11px "Aptos", "Segoe UI", sans-serif; pointer-events: none; }}
.graph-group-label {{ fill: #778690; font: 700 12px "Aptos", "Segoe UI", sans-serif; text-anchor: middle; }}
.graph-node:focus circle, .graph-node:hover circle {{ stroke: white; stroke-width: 3; }}
.graph-detail {{ min-height: 78px; padding: 16px 20px; border-top: 1px solid #34414b; color: #c7d0d5; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 20px; align-items: center; }}
.graph-detail strong {{ color: white; display: block; overflow-wrap: anywhere; }}
.graph-detail-meta {{ color: #9da8af; font-size: 12px; margin-top: 4px; }}
.graph-action {{ color: white; border: 1px solid #69767f; padding: 7px 10px; font-size: 12px; white-space: nowrap; }}
.module-list {{ border-top: 1px solid var(--ink); }}
.module-row {{
  display: grid;
  grid-template-columns: minmax(150px, 1fr) minmax(180px, 2fr) 88px;
  align-items: center;
  gap: 24px;
  min-height: 62px;
  border-bottom: 1px solid var(--soft-rule);
}}
.module-name {{ font-weight: 650; overflow-wrap: anywhere; }}
.bar-track {{ height: 8px; background: #dce3e7; overflow: hidden; }}
.bar {{ height: 100%; background: var(--cobalt); min-width: 4px; }}
.file-count {{ text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }}
.empty {{ padding: 24px 0; color: var(--muted); border-top: 1px solid var(--rule); }}
.task-list {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); border-top: 1px solid var(--ink); }}
.task {{ min-height: 130px; padding: 20px 24px 22px 0; border-bottom: 1px solid var(--rule); }}
.task:nth-child(even) {{ border-left: 1px solid var(--rule); padding-left: 24px; }}
.task-state {{ color: var(--cobalt); font-size: 12px; font-weight: 700; margin-bottom: 12px; }}
.task-title {{ font-size: 18px; font-weight: 610; line-height: 1.35; }}
.task-category {{ margin-top: 8px; color: var(--muted); font-size: 13px; }}
.decision-list {{ counter-reset: decisions; border-top: 1px solid var(--ink); }}
.decision {{
  counter-increment: decisions;
  display: grid;
  grid-template-columns: 64px minmax(160px, .8fr) minmax(260px, 1.5fr);
  gap: 28px;
  padding: 26px 0;
  border-bottom: 1px solid var(--rule);
}}
.decision::before {{ content: counter(decisions, decimal-leading-zero); color: var(--signal); font-weight: 750; font-variant-numeric: tabular-nums; }}
.decision-title {{ font-size: 17px; font-weight: 650; line-height: 1.35; }}
.decision-rationale {{ color: #47545d; max-width: 72ch; }}
.note-list {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1px; background: var(--rule); border: 1px solid var(--rule); }}
.note {{ background: var(--surface); padding: 22px; min-height: 110px; }}
.note-id {{ color: var(--signal); font-size: 12px; font-weight: 700; margin-bottom: 10px; }}
.changes {{ display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--rule); }}
.change {{ padding: 17px 20px; background: var(--surface); }}
.change + .change {{ border-left: 1px solid var(--rule); }}
.change strong {{ display: block; font-size: 24px; }}
.change span {{ color: var(--muted); font-size: 12px; }}
.catalog-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); border: 1px solid var(--rule); background: var(--rule); gap: 1px; }}
.catalog-column {{ background: var(--surface); padding: 22px; min-height: 220px; }}
.catalog-column h3 {{ margin: 0 0 18px; font-size: 16px; }}
.catalog-list {{ list-style: none; margin: 0; padding: 0; }}
.catalog-item {{ padding: 12px 0; border-top: 1px solid var(--soft-rule); }}
.catalog-item:first-child {{ border-top: 0; padding-top: 0; }}
.catalog-title {{ font-weight: 650; overflow-wrap: anywhere; }}
.catalog-meta {{ color: var(--muted); font-size: 12px; margin-top: 3px; overflow-wrap: anywhere; }}
.history-filter {{ display: flex; align-items: center; gap: 10px; }}
.history-filter input {{ border: 1px solid var(--rule); background: var(--surface); color: var(--ink); padding: 7px 9px; }}
.history-list {{ border-top: 1px solid var(--ink); }}
.history-event {{ display: grid; grid-template-columns: 160px minmax(0, 1fr); gap: 28px; padding: 22px 0; border-bottom: 1px solid var(--rule); }}
.history-date {{ font-weight: 650; }}
.history-counts {{ display: flex; gap: 16px; color: var(--muted); font-size: 13px; margin-bottom: 10px; }}
.history-files {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.history-file {{ padding: 3px 7px; background: var(--surface); border: 1px solid var(--soft-rule); font-family: "Cascadia Code", Consolas, monospace; font-size: 11px; }}
.footer {{ display: flex; justify-content: space-between; gap: 24px; padding-top: 32px; color: var(--muted); font-size: 12px; }}
.footer strong {{ color: var(--ink); }}
[hidden] {{ display: none !important; }}
@media (max-width: 900px) {{
  .shell {{ padding-inline: 20px; }}
  .masthead {{ grid-template-columns: 88px minmax(0, 1fr); min-height: auto; }}
  .snapshot {{ grid-column: 2; gap: 8px; }}
  .metrics {{ grid-template-columns: repeat(3, 1fr); }}
  .metric:nth-child(4) {{ border-left: 0; }}
  .metric:nth-child(n+4) {{ border-top: 1px solid var(--rule); }}
  .workspace {{ grid-template-columns: 1fr; gap: 30px; }}
  .context-rail {{ grid-template-columns: 1fr 1fr; }}
  .agent-context {{ grid-column: 1 / -1; border-left: 0; border-top: 1px solid var(--rule); padding-left: 0; }}
  .index {{ position: static; display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
}}
@media (max-width: 620px) {{
  .masthead {{ display: block; padding: 28px 0; }}
  .mark {{ width: 56px; height: 56px; margin-bottom: 48px; }}
  .project-name {{ font-size: 48px; }}
  .snapshot {{ margin-top: 30px; gap: 8px; }}
  .metrics {{ grid-template-columns: 1fr 1fr; }}
  .context-rail {{ grid-template-columns: 1fr; }}
  .context-control + .context-control, .agent-context {{ border-left: 0; border-top: 1px solid var(--rule); padding-left: 0; }}
  .agent-context {{ grid-column: auto; }}
  .metric:nth-child(odd) {{ border-left: 0; }}
  .metric:nth-child(n+3) {{ border-top: 1px solid var(--rule); }}
  .metric {{ min-height: 112px; padding: 18px 12px 18px 0; }}
  .metric + .metric {{ padding-left: 14px; }}
  .index {{ display: block; }}
  .section-head {{ display: block; }}
  .search {{ margin-top: 18px; }}
  .module-row {{ grid-template-columns: 1fr 58px; gap: 12px; padding: 12px 0; }}
  .bar-track {{ grid-column: 1 / -1; grid-row: 2; }}
  .task-list, .note-list {{ grid-template-columns: 1fr; }}
  .catalog-grid {{ grid-template-columns: 1fr; }}
  .task:nth-child(even) {{ border-left: 0; padding-left: 0; }}
  .decision {{ grid-template-columns: 40px 1fr; gap: 14px; }}
  .decision-rationale {{ grid-column: 2; }}
  .changes {{ grid-template-columns: 1fr; }}
  .change + .change {{ border-left: 0; border-top: 1px solid var(--rule); }}
  .footer {{ display: block; }}
  .graph-toolbar, .graph-detail {{ display: block; }}
  .graph-toolbar .search {{ margin-top: 12px; }}
  .graph-action {{ display: inline-block; margin-top: 12px; }}
  .history-event {{ grid-template-columns: 1fr; gap: 8px; }}
}}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
</style>
</head>
<body>
<div class="topline"></div>
<div class="shell">
  <header class="masthead">
    <div class="mark" aria-label="Agent Memory">AM</div>
    <div>
      <h1 class="project-name" id="projectName"></h1>
      <p class="project-description" id="projectDescription"></p>
    </div>
    <div class="snapshot">
      <div class="snapshot-state"><span class="pulse" aria-hidden="true"></span><span>Memory snapshot ready</span></div>
      <div class="snapshot-time" id="updated"></div>
    </div>
  </header>

  <section class="metrics" aria-label="Project summary">
    <div class="metric"><div class="metric-value" id="fileCount">0</div><div class="metric-label">Files indexed</div></div>
    <div class="metric"><div class="metric-value" id="linkCount">0</div><div class="metric-label">Resolved links</div></div>
    <div class="metric"><div class="metric-value" id="connectedCount">0</div><div class="metric-label">Connected files</div></div>
    <div class="metric"><div class="metric-value" id="agentCount">0</div><div class="metric-label">AI agents</div></div>
    <div class="metric"><div class="metric-value" id="chatCount">0</div><div class="metric-label">Tracked chats</div></div>
    <div class="metric"><div class="metric-value" id="projectCount">0</div><div class="metric-label">Tracked projects</div></div>
  </section>

  <section class="context-rail" aria-label="Active memory context">
    <div class="context-control"><label for="projectSelect">Project</label><select id="projectSelect"></select></div>
    <div class="context-control"><label for="agentSelect">AI agent</label><select id="agentSelect"></select></div>
    <div class="agent-context" id="agentContext"><strong>No agent selected</strong><span>Choose an agent to view its instruction and chat context.</span></div>
  </section>

  <div class="workspace">
    <aside class="index" aria-label="Project index">
      <div class="index-block">
        <h2 class="section-title">Technology</h2>
        <div class="stack-list" id="stack"></div>
      </div>
      <div class="index-block">
        <h2 class="section-title">Start here</h2>
        <ul class="path-list" id="entrypoints"></ul>
      </div>
      <nav class="index-block" aria-label="Dashboard sections">
        <h2 class="section-title">Index</h2>
        <ul class="jump-list">
          <li><a href="#graph">File graph</a></li>
          <li><a href="#repository">Repository map</a></li>
          <li><a href="#catalog">Agents and projects</a></li>
          <li><a href="#history">Edit history</a></li>
          <li><a href="#work">Active work</a></li>
          <li><a href="#decisions">Decisions</a></li>
          <li><a href="#notes">Notes</a></li>
        </ul>
      </nav>
    </aside>

    <main class="main-column">
      <section class="section" id="graph">
        <div class="section-head"><div><h2>File relationship graph</h2><div class="section-meta" id="graphMeta"></div></div></div>
        <div class="graph-shell">
          <div class="graph-toolbar">
            <div class="graph-legend">Each node is a file. Lines are resolved imports, includes, assets, or links.</div>
            <label class="search"><span aria-hidden="true">⌕</span><input id="graphSearch" type="search" placeholder="Find a file node" aria-label="Find a file node"></label>
          </div>
          <div class="graph-stage" id="graphStage" aria-label="Interactive file relationship graph"></div>
          <div class="graph-detail" id="graphDetail"><div><strong>Select a file node</strong><div class="graph-detail-meta">Choose a node to inspect its path, type, and connections.</div></div></div>
        </div>
      </section>

      <section class="section" id="repository">
        <div class="section-head">
          <div><h2>Repository map</h2><div class="section-meta" id="moduleMeta"></div></div>
          <label class="search"><span aria-hidden="true">⌕</span><input id="moduleSearch" type="search" placeholder="Filter modules" aria-label="Filter repository modules"></label>
        </div>
        <div class="module-list" id="modules"></div>
        <div class="empty" id="moduleEmpty" hidden>No modules match that filter.</div>
      </section>

      <section class="section" id="catalog">
        <div class="section-head"><h2>Memory catalogue</h2><div class="section-meta">Explicitly tracked, never silently scraped</div></div>
        <div class="catalog-grid">
          <div class="catalog-column"><h3>AI agents</h3><ul class="catalog-list" id="agentList"></ul></div>
          <div class="catalog-column"><h3>Projects</h3><ul class="catalog-list" id="projectList"></ul></div>
          <div class="catalog-column"><h3>Chats</h3><ul class="catalog-list" id="chatList"></ul></div>
        </div>
      </section>

      <section class="section" id="history">
        <div class="section-head">
          <div><h2>Edit history</h2><div class="section-meta" id="historyMeta"></div></div>
          <label class="history-filter">Date <input id="historyDate" type="date" aria-label="Filter edit history by date"></label>
        </div>
        <div class="history-list" id="historyList"></div>
        <div class="empty" id="historyEmpty" hidden>No scans match that date.</div>
      </section>

      <section class="section" id="work">
        <div class="section-head"><h2>Active work</h2><div class="section-meta" id="taskMeta"></div></div>
        <div class="task-list" id="tasks"></div>
        <div class="empty" id="taskEmpty" hidden>No active tasks. Add one with the memory CLI when follow-up work appears.</div>
      </section>

      <section class="section" id="decisions">
        <div class="section-head"><h2>Decision ledger</h2><div class="section-meta">Oldest to newest</div></div>
        <div class="decision-list" id="decisionList"></div>
        <div class="empty" id="decisionEmpty" hidden>No decisions recorded yet.</div>
      </section>

      <section class="section" id="notes">
        <div class="section-head"><h2>Durable notes</h2><div class="section-meta">Facts worth carrying forward</div></div>
        <div class="note-list" id="noteList"></div>
        <div class="empty" id="noteEmpty" hidden>No durable notes recorded yet.</div>
      </section>

      <section class="section">
        <div class="section-head"><h2>Since the previous scan</h2></div>
        <div class="changes">
          <div class="change"><strong id="addedCount">0</strong><span>Added</span></div>
          <div class="change"><strong id="changedCount">0</strong><span>Changed</span></div>
          <div class="change"><strong id="removedCount">0</strong><span>Removed</span></div>
        </div>
      </section>
    </main>
  </div>

  <footer class="footer"><span><strong>Agent Memory</strong> / local-first relationship context for any AI agent</span><span>File contents and transcript text are never embedded in this dashboard.</span></footer>
</div>
<script>
let memory = {payload};
const rootMemory = memory;
const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[character]));
const formatBytes = bytes => {{
  const value = Number(bytes || 0);
  if (value < 1024) return `${{value}} B`;
  if (value < 1048576) return `${{(value / 1024).toFixed(value < 10240 ? 1 : 0)}} KB`;
  return `${{(value / 1048576).toFixed(1)}} MB`;
}};
const formatDate = value => {{
  if (!value) return 'This project has not been scanned yet.';
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? `Last scanned ${{value}}` : `Last scanned ${{new Intl.DateTimeFormat(undefined, {{dateStyle:'medium', timeStyle:'short'}}).format(date)}}`;
}};

let project = memory.project || {{}};
let summary = memory.summary || {{}};
let architecture = memory.architecture || {{}};
let graph = memory.graph || {{nodes:[], edges:[], summary:{{}}}};
let activeTasks = (memory.tasks || []).filter(task => !['done','completed','cancelled'].includes(String(task.status || 'pending').toLowerCase()));
let modules = architecture.modules || [];
let maxFiles = Math.max(1, ...modules.map(module => Number(module.file_count || 0)));

byId('projectName').textContent = project.display_name || project.name || 'Untitled project';
byId('projectDescription').textContent = project.description || architecture.overview || 'Project structure, decisions, and active work in one durable index.';
byId('updated').textContent = formatDate(project.last_scanned);
byId('fileCount').textContent = Number(summary.file_count || 0).toLocaleString();
byId('linkCount').textContent = Number(graph.summary?.edge_count || 0).toLocaleString();
byId('connectedCount').textContent = Number(graph.summary?.connected_files || 0).toLocaleString();
byId('agentCount').textContent = (memory.agents || []).length.toLocaleString();
byId('chatCount').textContent = (memory.chats || []).length.toLocaleString();
byId('projectCount').textContent = (memory.projects || []).length.toLocaleString();

const stack = project.tech_stack || [];
byId('stack').innerHTML = stack.length ? stack.map(item => `<span class="stack-item">${{escapeHtml(item)}}</span>`).join('') : '<span class="section-meta">Not detected</span>';
const entrypoints = memory.entrypoints || [];
byId('entrypoints').innerHTML = entrypoints.length ? entrypoints.map(path => `<li><code>${{escapeHtml(path)}}</code></li>`).join('') : '<li class="section-meta">No entrypoints detected</li>';

function renderGraph() {{
  const allNodes = graph.nodes || [];
  const ranked = allNodes.slice().sort((a, b) => Number(b.connections || 0) - Number(a.connections || 0) || String(a.path).localeCompare(String(b.path)));
  const visibleNodes = ranked.slice(0, 250);
  const visibleIds = new Set(visibleNodes.map(node => node.id));
  const visibleEdges = (graph.edges || []).filter(edge => visibleIds.has(edge.source) && visibleIds.has(edge.target));
  const groups = new Map();
  visibleNodes.forEach(node => {{
    const key = node.module || 'root';
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(node);
  }});
  const groupEntries = [...groups.entries()];
  const columns = Math.max(1, Math.ceil(Math.sqrt(groupEntries.length * 1.7)));
  const rows = Math.max(1, Math.ceil(groupEntries.length / columns));
  const positions = new Map();
  groupEntries.forEach(([moduleName, nodes], groupIndex) => {{
    const column = groupIndex % columns;
    const row = Math.floor(groupIndex / columns);
    const centerX = ((column + .5) / columns) * 1000;
    const centerY = ((row + .5) / rows) * 500 + 20;
    const radius = Math.min(118, 48 + nodes.length * 7);
    nodes.forEach((node, index) => {{
      const angle = nodes.length === 1 ? 0 : (Math.PI * 2 * index / nodes.length) - Math.PI / 2;
      const ring = nodes.length === 1 ? 0 : radius * (.82 + .18 * (index % 2));
      positions.set(node.id, {{x: centerX + Math.cos(angle) * ring, y: centerY + Math.sin(angle) * ring}});
    }});
  }});
  const lines = visibleEdges.map(edge => {{
    const source = positions.get(edge.source), target = positions.get(edge.target);
    return source && target ? `<line class="graph-edge" data-source="${{escapeHtml(edge.source)}}" data-target="${{escapeHtml(edge.target)}}" x1="${{source.x.toFixed(1)}}" y1="${{source.y.toFixed(1)}}" x2="${{target.x.toFixed(1)}}" y2="${{target.y.toFixed(1)}}"><title>${{escapeHtml(edge.kind)}}: ${{escapeHtml(edge.source)}} → ${{escapeHtml(edge.target)}}</title></line>` : '';
  }}).join('');
  const groupLabels = groupEntries.map(([moduleName, nodes], groupIndex) => {{
    const column = groupIndex % columns;
    const row = Math.floor(groupIndex / columns);
    const x = ((column + .5) / columns) * 1000;
    const y = ((row + .5) / rows) * 500 - 105;
    return `<text class="graph-group-label" x="${{x.toFixed(1)}}" y="${{Math.max(22, y).toFixed(1)}}">${{escapeHtml(moduleName)}}</text>`;
  }}).join('');
  const nodes = visibleNodes.map((node, index) => {{
    const point = positions.get(node.id);
    const connections = Number(node.connections || 0);
    const radius = 4.5 + Math.min(7, Math.sqrt(connections) * 2.2);
    const state = connections >= 4 ? 'is-hub' : connections > 0 ? 'is-connected' : '';
    const label = (connections > 0 || visibleNodes.length < 10) ? `<text x="${{(point.x + radius + 4).toFixed(1)}}" y="${{(point.y + 4).toFixed(1)}}">${{escapeHtml(node.label)}}</text>` : '';
    return `<g class="graph-node ${{state}}" tabindex="0" role="button" data-path="${{escapeHtml(node.path)}}" aria-label="${{escapeHtml(node.path)}}, ${{connections}} connections"><circle cx="${{point.x.toFixed(1)}}" cy="${{point.y.toFixed(1)}}" r="${{radius.toFixed(1)}}"><title>${{escapeHtml(node.path)}}</title></circle>${{label}}</g>`;
  }}).join('');
  byId('graphStage').innerHTML = `<svg viewBox="0 0 1000 540" role="img" aria-label="File relationship graph">${{groupLabels}}${{lines}}${{nodes}}</svg>`;
  byId('graphMeta').textContent = `${{allNodes.length}} nodes / ${{(graph.edges || []).length}} links${{allNodes.length > 250 ? ' / showing 250 most connected' : ''}}`;
}}

function selectGraphNode(path) {{
  const node = (graph.nodes || []).find(item => item.path === path);
  if (!node) return;
  byId('graphDetail').innerHTML = `<div><strong>${{escapeHtml(node.path)}}</strong><div class="graph-detail-meta">${{escapeHtml(node.language)}} / ${{Number(node.connections || 0)}} connections / ${{formatBytes(node.size_bytes)}}</div></div><code class="graph-action">related "${{escapeHtml(node.path)}}"</code>`;
}}

renderGraph();
byId('graphStage').addEventListener('click', event => {{ const node = event.target.closest('.graph-node'); if (node) selectGraphNode(node.dataset.path); }});
byId('graphStage').addEventListener('keydown', event => {{ const node = event.target.closest('.graph-node'); if (node && (event.key === 'Enter' || event.key === ' ')) {{ event.preventDefault(); selectGraphNode(node.dataset.path); }} }});
byId('graphSearch').addEventListener('input', event => {{
  const query = event.target.value.trim().toLowerCase();
  byId('graphStage').querySelectorAll('.graph-node').forEach(node => {{ node.style.opacity = !query || node.dataset.path.toLowerCase().includes(query) ? '1' : '.12'; }});
}});

function renderModules(query = '') {{
  const normalized = query.trim().toLowerCase();
  const visible = modules.filter(module => String(module.name || '').toLowerCase().includes(normalized));
  byId('modules').innerHTML = visible.map(module => {{
    const count = Number(module.file_count || 0);
    const width = Math.max(2, (count / maxFiles) * 100);
    return `<div class="module-row"><div class="module-name">${{escapeHtml(module.name)}}</div><div class="bar-track" aria-hidden="true"><div class="bar" style="width:${{width}}%"></div></div><div class="file-count">${{count.toLocaleString()}} files</div></div>`;
  }}).join('');
  byId('moduleMeta').textContent = `${{visible.length}} of ${{modules.length}} modules`;
  byId('moduleEmpty').hidden = visible.length !== 0;
}}
renderModules();
byId('moduleSearch').addEventListener('input', event => renderModules(event.target.value));

let agents = memory.agents || [];
byId('agentList').innerHTML = agents.length ? agents.map(agent => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(agent.name)}}</div><div class="catalog-meta">${{escapeHtml(agent.status || 'detected')}} / ${{escapeHtml(agent.instruction_file || 'No instruction file')}}</div></li>`).join('') : '<li class="catalog-meta">No AI agents detected. Run <code>enable-agent</code> to add one.</li>';
let projects = memory.projects || [];
byId('projectList').innerHTML = projects.length ? projects.map(item => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(item.name)}}</div><div class="catalog-meta">${{Number(item.file_count || 0)}} files / ${{Number(item.edge_count || 0)}} links<br>${{escapeHtml(item.path)}}</div></li>`).join('') : '<li class="catalog-meta">No projects tracked yet.</li>';
let chats = memory.chats || [];
byId('chatList').innerHTML = chats.length ? chats.slice().reverse().map(chat => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(chat.title)}}</div><div class="catalog-meta">${{escapeHtml(chat.agent)}} / ${{escapeHtml(chat.summary)}}</div></li>`).join('') : '<li class="catalog-meta">No chat metadata imported. Transcripts are never collected automatically.</li>';

let history = memory.history || [];
function renderHistory(date = '') {{
  const visible = history.slice().reverse().filter(event => !date || String(event.scanned_at || '').startsWith(date));
  byId('historyList').innerHTML = visible.map(event => {{
    const files = [...(event.added || []).map(path => ['+', path]), ...(event.changed || []).map(path => ['~', path]), ...(event.removed || []).map(path => ['−', path])];
    const fileMarkup = files.slice(0, 18).map(([prefix, path]) => `<span class="history-file">${{prefix}} ${{escapeHtml(path)}}</span>`).join('');
    const overflow = files.length > 18 ? `<span class="history-file">+${{files.length - 18}} more</span>` : '';
    return `<article class="history-event"><div class="history-date">${{escapeHtml(formatDate(event.scanned_at).replace('Last scanned ', ''))}}</div><div><div class="history-counts"><span>${{(event.added || []).length}} added</span><span>${{(event.changed || []).length}} changed</span><span>${{(event.removed || []).length}} removed</span></div><div class="history-files">${{fileMarkup}}${{overflow}}</div></div></article>`;
  }}).join('');
  byId('historyMeta').textContent = `${{visible.length}} of ${{history.length}} scans`;
  byId('historyEmpty').hidden = visible.length !== 0;
}}
renderHistory();
byId('historyDate').addEventListener('input', event => renderHistory(event.target.value));

byId('taskMeta').textContent = `${{activeTasks.length}} open`;
byId('tasks').innerHTML = activeTasks.map(task => `<article class="task"><div class="task-state">${{escapeHtml(task.status || 'pending')}}</div><div class="task-title">${{escapeHtml(task.title)}}</div><div class="task-category">${{escapeHtml(task.category || 'General')}}</div></article>`).join('');
byId('taskEmpty').hidden = activeTasks.length !== 0;

let decisions = memory.decisions || [];
byId('decisionList').innerHTML = decisions.map(decision => `<article class="decision"><div class="decision-title">${{escapeHtml(decision.title)}}</div><div class="decision-rationale">${{escapeHtml(decision.rationale)}}</div></article>`).join('');
byId('decisionEmpty').hidden = decisions.length !== 0;

let notes = memory.notes || [];
byId('noteList').innerHTML = notes.map(note => `<article class="note"><div class="note-id">Note ${{escapeHtml(note.id)}}</div><div>${{escapeHtml(note.text)}}</div></article>`).join('');
byId('noteEmpty').hidden = notes.length !== 0;

let changes = summary.changes || {{}};
byId('addedCount').textContent = (changes.added || []).length.toLocaleString();
byId('changedCount').textContent = (changes.changed || []).length.toLocaleString();
byId('removedCount').textContent = (changes.removed || []).length.toLocaleString();

const projectChoices = [
  {{key: '__current__', name: rootMemory.project?.display_name || rootMemory.project?.name || 'Current project', memory: rootMemory}},
  ...(rootMemory.projects || []).filter(item => !item.is_current && (item.snapshot || item.dashboard_file)).map((item, index) => ({{key: `tracked-${{index}}`, name: item.name, memory: item.snapshot, href: item.dashboard_file}}))
];
byId('projectSelect').innerHTML = projectChoices.map(choice => `<option value="${{escapeHtml(choice.key)}}">${{escapeHtml(choice.name)}}</option>`).join('');

function renderAgentSelection(preferred = '__all__') {{
  const options = [`<option value="__all__">All agents</option>`, ...agents.map(agent => `<option value="${{escapeHtml(agent.key || agent.id || agent.name)}}">${{escapeHtml(agent.name)}}</option>`)];
  byId('agentSelect').innerHTML = options.join('');
  const valid = [...byId('agentSelect').options].some(option => option.value === preferred);
  byId('agentSelect').value = valid ? preferred : '__all__';
  renderAgentContext();
}}

function renderAgentContext() {{
  const selected = byId('agentSelect').value;
  const agent = agents.find(item => String(item.key || item.id || item.name) === selected);
  const visibleChats = agent ? chats.filter(chat => String(chat.agent || '').toLowerCase() === String(agent.name || '').toLowerCase()) : chats;
  if (agent) {{
    byId('agentContext').innerHTML = `<strong>${{escapeHtml(agent.name)}}</strong><span>${{escapeHtml(agent.status || 'detected')}} / ${{escapeHtml(agent.instruction_file || 'No instruction file')}} / ${{visibleChats.length}} tracked chats</span>`;
  }} else {{
    byId('agentContext').innerHTML = `<strong>All agents</strong><span>${{agents.length}} available in this project / ${{chats.length}} tracked chats</span>`;
  }}
  byId('chatList').innerHTML = visibleChats.length ? visibleChats.slice().reverse().map(chat => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(chat.title)}}</div><div class="catalog-meta">${{escapeHtml(chat.agent)}} / ${{escapeHtml(chat.summary)}}</div></li>`).join('') : `<li class="catalog-meta">${{agent ? `No chats tracked for ${{escapeHtml(agent.name)}}.` : 'No chat metadata imported. Transcripts are never collected automatically.'}}</li>`;
}}

function applyMemory(nextMemory) {{
  memory = nextMemory || {{}};
  project = memory.project || {{}};
  summary = memory.summary || {{}};
  architecture = memory.architecture || {{}};
  graph = memory.graph || {{nodes:[], edges:[], summary:{{}}}};
  activeTasks = (memory.tasks || []).filter(task => !['done','completed','cancelled'].includes(String(task.status || 'pending').toLowerCase()));
  modules = architecture.modules || [];
  maxFiles = Math.max(1, ...modules.map(module => Number(module.file_count || 0)));
  agents = memory.agents || [];
  chats = memory.chats || [];
  history = memory.history || [];
  decisions = memory.decisions || [];
  notes = memory.notes || [];
  changes = summary.changes || {{}};
  projects = rootMemory.projects || [];

  byId('projectName').textContent = project.display_name || project.name || 'Untitled project';
  byId('projectDescription').textContent = project.description || architecture.overview || 'Project structure, decisions, and active work in one durable index.';
  byId('updated').textContent = formatDate(project.last_scanned);
  byId('fileCount').textContent = Number(summary.file_count || 0).toLocaleString();
  byId('linkCount').textContent = Number(graph.summary?.edge_count || 0).toLocaleString();
  byId('connectedCount').textContent = Number(graph.summary?.connected_files || 0).toLocaleString();
  byId('agentCount').textContent = agents.length.toLocaleString();
  byId('chatCount').textContent = chats.length.toLocaleString();
  byId('projectCount').textContent = projects.length.toLocaleString();

  const stack = project.tech_stack || [];
  byId('stack').innerHTML = stack.length ? stack.map(item => `<span class="stack-item">${{escapeHtml(item)}}</span>`).join('') : '<span class="section-meta">Not detected</span>';
  const entrypoints = memory.entrypoints || [];
  byId('entrypoints').innerHTML = entrypoints.length ? entrypoints.map(path => `<li><code>${{escapeHtml(path)}}</code></li>`).join('') : '<li class="section-meta">No entrypoints detected</li>';

  byId('graphSearch').value = '';
  byId('moduleSearch').value = '';
  byId('historyDate').value = '';
  byId('graphDetail').innerHTML = '<div><strong>Select a file node</strong><div class="graph-detail-meta">Choose a node to inspect its path, type, and connections.</div></div>';
  renderGraph();
  renderModules();
  renderHistory();

  byId('agentList').innerHTML = agents.length ? agents.map(agent => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(agent.name)}}</div><div class="catalog-meta">${{escapeHtml(agent.status || 'detected')}} / ${{escapeHtml(agent.instruction_file || 'No instruction file')}}</div></li>`).join('') : '<li class="catalog-meta">No AI agents detected. Run <code>enable-agent</code> to add one.</li>';
  byId('projectList').innerHTML = projects.length ? projects.map(item => `<li class="catalog-item"><div class="catalog-title">${{escapeHtml(item.name)}}</div><div class="catalog-meta">${{Number(item.file_count || 0)}} files / ${{Number(item.edge_count || 0)}} links<br>${{escapeHtml(item.path)}}</div></li>`).join('') : '<li class="catalog-meta">No projects tracked yet.</li>';
  renderAgentSelection();

  byId('taskMeta').textContent = `${{activeTasks.length}} open`;
  byId('tasks').innerHTML = activeTasks.map(task => `<article class="task"><div class="task-state">${{escapeHtml(task.status || 'pending')}}</div><div class="task-title">${{escapeHtml(task.title)}}</div><div class="task-category">${{escapeHtml(task.category || 'General')}}</div></article>`).join('');
  byId('taskEmpty').hidden = activeTasks.length !== 0;
  byId('decisionList').innerHTML = decisions.map(decision => `<article class="decision"><div class="decision-title">${{escapeHtml(decision.title)}}</div><div class="decision-rationale">${{escapeHtml(decision.rationale)}}</div></article>`).join('');
  byId('decisionEmpty').hidden = decisions.length !== 0;
  byId('noteList').innerHTML = notes.map(note => `<article class="note"><div class="note-id">Note ${{escapeHtml(note.id)}}</div><div>${{escapeHtml(note.text)}}</div></article>`).join('');
  byId('noteEmpty').hidden = notes.length !== 0;
  byId('addedCount').textContent = (changes.added || []).length.toLocaleString();
  byId('changedCount').textContent = (changes.changed || []).length.toLocaleString();
  byId('removedCount').textContent = (changes.removed || []).length.toLocaleString();
}}

byId('projectSelect').addEventListener('change', event => {{
  const choice = projectChoices.find(item => item.key === event.target.value);
  if (!choice) return;
  if (choice.href) window.location.href = choice.href;
  else applyMemory(choice.memory);
}});
byId('agentSelect').addEventListener('change', renderAgentContext);
applyMemory(rootMemory);
</script>
</body>
</html>'''
