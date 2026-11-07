"""Self-contained project-memory dashboard generator."""

from __future__ import annotations

import html
import json
from typing import Any


def render_dashboard(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    name = html.escape(data.get("project", {}).get("name", "Project Memory"))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — Project Memory</title>
<style>
:root{{--bg:#081018;--panel:#101c28;--line:#23364a;--text:#e6edf3;--muted:#8ca0b3;--accent:#62d5b2;--blue:#6cb6ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,Segoe UI,sans-serif}}main{{max-width:1180px;margin:auto;padding:32px 20px 60px}}header{{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:24px}}h1{{margin:0;font-size:clamp(28px,5vw,52px);letter-spacing:-.04em}}.eyebrow{{color:var(--accent);text-transform:uppercase;letter-spacing:.16em;font-size:12px;font-weight:700}}.muted{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:14px}}.card{{grid-column:span 4;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}.wide{{grid-column:span 8}}.full{{grid-column:1/-1}}.metric{{font-size:30px;font-weight:750;color:var(--blue)}}h2{{font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin:0 0 14px}}ul{{list-style:none;padding:0;margin:0}}li{{padding:8px 0;border-top:1px solid var(--line)}}li:first-child{{border:0}}code{{color:var(--accent)}}.pill{{display:inline-block;background:#172c34;border:1px solid #28504d;color:var(--accent);padding:4px 9px;border-radius:99px;margin:3px;font-size:12px}}.status{{font-size:11px;text-transform:uppercase;color:var(--blue)}}@media(max-width:780px){{.card,.wide{{grid-column:1/-1}}header{{display:block}}}}
</style></head><body><main>
<header><div><div class="eyebrow">Agent-ready project memory</div><h1 id="name"></h1><div class="muted" id="description"></div></div><div class="muted" id="updated"></div></header>
<section class="grid"><article class="card"><h2>Files indexed</h2><div class="metric" id="files"></div></article><article class="card"><h2>Active tasks</h2><div class="metric" id="taskCount"></div></article><article class="card"><h2>Decisions</h2><div class="metric" id="decisionCount"></div></article><article class="card wide"><h2>Technology</h2><div id="stack"></div></article><article class="card"><h2>Start here</h2><ul id="entrypoints"></ul></article><article class="card wide"><h2>Repository map</h2><ul id="modules"></ul></article><article class="card"><h2>Tasks</h2><ul id="tasks"></ul></article><article class="card full"><h2>Architectural decisions</h2><ul id="decisions"></ul></article></section>
</main><script>
const d={payload};const q=id=>document.getElementById(id);const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));q('name').textContent=d.project?.name||'Project';q('description').textContent=d.project?.description||'No description recorded yet.';q('updated').textContent='Updated '+(d.project?.last_scanned||'never');q('files').textContent=(d.summary?.file_count||0).toLocaleString();const active=(d.tasks||[]).filter(t=>!['done','completed','cancelled'].includes(t.status));q('taskCount').textContent=active.length;q('decisionCount').textContent=(d.decisions||[]).length;q('stack').innerHTML=(d.project?.tech_stack||[]).map(x=>`<span class="pill">${{esc(x)}}</span>`).join('')||'<span class="muted">Not detected</span>';q('entrypoints').innerHTML=(d.entrypoints||[]).map(x=>`<li><code>${{esc(x)}}</code></li>`).join('')||'<li class="muted">No entrypoints detected</li>';q('modules').innerHTML=(d.architecture?.modules||[]).map(x=>`<li><strong>${{esc(x.name)}}</strong> <span class="muted">${{x.file_count}} files</span></li>`).join('');q('tasks').innerHTML=active.map(x=>`<li><span class="status">${{esc(x.status||'pending')}}</span><br>${{esc(x.title)}}</li>`).join('')||'<li class="muted">No active tasks</li>';q('decisions').innerHTML=(d.decisions||[]).slice().reverse().map(x=>`<li><strong>${{esc(x.title)}}</strong><br><span class="muted">${{esc(x.rationale)}}</span></li>`).join('')||'<li class="muted">No decisions recorded</li>';
</script></body></html>'''
