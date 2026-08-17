"""
build_html.py
Generate a single self-contained HTML page.
"""

import json
from datetime import datetime

# Load data
with open("output/pass_2.json") as f:
    apps = json.load(f)

# ===== HEADLINE FINDINGS (from Phase 5) =====
headlines = [
    "OAuth2 dominates (21%), followed by API keys (15%) – but 49% of apps still use 'unknown' auth, highlighting documentation gaps.",
    "Only 29% of apps are self-serve – 71% are gated behind paid plans, partner approval, or sales.",
    "67% of apps are buildable today; the main blocker (30%) is lack of public API or enterprise gating.",
    "Composio already ships toolkits for 60/100 apps – these are immediate, drop-in wins for agent integration.",
    "CRM & Sales is the easiest category (80% self-serve, 80% buildable), while Finance and AI/Research are the hardest.",
]

# Prepare data for substitution
today = datetime.now().strftime('%Y-%m-%d')
app_data_json = json.dumps(apps, indent=2)
headlines_html = "\n".join(f"<li>🔹 {h}</li>" for h in headlines)

# HTML template with {placeholders} for substitution
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Product Ops – App Research Case Study</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f6f9fc;
      color: #1e293b;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }}
    h1 {{
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
    }}
    .sub {{ color: #64748b; margin-bottom: 2rem; }}
    .findings {{
      background: #ffffff;
      border-radius: 12px;
      padding: 1.5rem 2rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      border-left: 6px solid #2563eb;
      margin-bottom: 2rem;
    }}
    .findings h2 {{ font-size: 1.1rem; color: #2563eb; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }}
    .findings ul {{ list-style: none; padding: 0; }}
    .findings li {{
      padding: 0.4rem 0;
      border-bottom: 1px solid #f1f5f9;
      font-weight: 500;
    }}
    .findings li:last-child {{ border: 0; }}
    .findings li span {{ font-weight: 400; color: #334155; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin: 2rem 0;
    }}
    .card {{
      background: #ffffff;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .card h3 {{ font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.3px; color: #64748b; margin-bottom: 0.5rem; }}
    .card .big {{ font-size: 2rem; font-weight: 700; color: #0f172a; }}
    .card .desc {{ font-size: 0.9rem; color: #475569; margin-top: 0.25rem; }}
    .badge {{
      display: inline-block;
      padding: 0.15rem 0.6rem;
      border-radius: 20px;
      font-size: 0.7rem;
      font-weight: 600;
      background: #e2e8f0;
      color: #1e293b;
    }}
    .badge-self {{ background: #dcfce7; color: #166534; }}
    .badge-gated {{ background: #fee2e2; color: #991b1b; }}
    .badge-yes {{ background: #dcfce7; color: #166534; }}
    .badge-partial {{ background: #fef9c3; color: #854d0e; }}
    .badge-no {{ background: #fee2e2; color: #991b1b; }}
    .badge-high {{ background: #dbeafe; color: #1e40af; }}
    .badge-medium {{ background: #fef9c3; color: #854d0e; }}
    .badge-low {{ background: #f1f5f9; color: #475569; }}
    .table-wrap {{
      background: #ffffff;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      margin-top: 2rem;
      overflow-x: auto;
    }}
    .table-wrap input {{
      width: 100%;
      padding: 0.6rem 1rem;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      margin-bottom: 1rem;
      font-size: 0.9rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }}
    th {{
      text-align: left;
      padding: 0.6rem 0.5rem;
      border-bottom: 2px solid #e2e8f0;
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    th:hover {{ background: #f8fafc; }}
    td {{
      padding: 0.5rem;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: middle;
    }}
    .evidence-link {{
      color: #2563eb;
      text-decoration: none;
      font-size: 0.75rem;
    }}
    .evidence-link:hover {{ text-decoration: underline; }}
    .footer {{
      margin-top: 2rem;
      color: #94a3b8;
      font-size: 0.8rem;
      text-align: center;
      border-top: 1px solid #e2e8f0;
      padding-top: 1.5rem;
    }}
    @media (max-width: 700px) {{
      body {{ padding: 1rem; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<h1>🧠 App Research Case Study</h1>
<div class="sub">100 apps researched · Composio take-home assignment · {today}</div>

<!-- Headline Findings -->
<div class="findings">
  <h2>📌 Key Findings</h2>
  <ul>
    {headlines_html}
  </ul>
</div>

<!-- Agent + Verification -->
<div class="grid">
  <div class="card">
    <h3>🤖 The Agent</h3>
    <p style="margin-bottom:0.5rem; font-size:0.95rem;">
      Built with <strong>Gemini</strong> + <strong>Composio catalog</strong>:
    </p>
    <ul style="padding-left:1.2rem; font-size:0.9rem; color:#334155; line-height:1.6;">
      <li>Tier 1: Composio toolkit lookup (ground-truth auth for 60 apps)</li>
      <li>Tier 2: Gemini (with retries) for one-liner, self-serve, API surface</li>
      <li>Human verification loop: 20 apps hand-checked</li>
    </ul>
  </div>
  <div class="card">
    <h3>✅ Verification</h3>
    <div class="big">30% → 100%</div>
    <div class="desc">Pass 1 (agent) vs Pass 2 (verified) on 20-app sample</div>
    <ul style="margin-top:0.75rem; padding-left:1.2rem; font-size:0.85rem; color:#334155; line-height:1.6;">
      <li><strong>Auth:</strong> 15% → 100%</li>
      <li><strong>Self-serve:</strong> 20% → 100%</li>
      <li><strong>API surface:</strong> 15% → 100%</li>
      <li><strong>Buildability:</strong> 70% → 100%</li>
    </ul>
  </div>
</div>

<!-- Full Table -->
<div class="table-wrap">
  <h2 style="font-size:1.1rem; margin-bottom:0.5rem;">📋 All 100 Apps</h2>
  <input type="text" id="searchInput" placeholder="🔍 Search by app name, category, auth…" oninput="filterTable()" />
  <div style="overflow-x:auto;">
    <table id="appTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">App</th>
          <th onclick="sortTable(1)">Category</th>
          <th onclick="sortTable(2)">Auth</th>
          <th onclick="sortTable(3)">Self‑Serve</th>
          <th onclick="sortTable(4)">API Surface</th>
          <th onclick="sortTable(5)">Buildability</th>
          <th onclick="sortTable(6)">Confidence</th>
          <th>Evidence</th>
        </tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
</div>

<div class="footer">
  Built for Composio · Source code and data available on request.
</div>

<script>
// The full dataset is injected here
const appData = {app_data};

function renderTable(data) {{
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';
  data.forEach(app => {{
    const tr = document.createElement('tr');
    
    const authStr = app.auth_methods && app.auth_methods.length ? app.auth_methods.join(', ') : 'unknown';
    
    let selfBadge = '<span class="badge badge-gated">Gated</span>';
    if (app.self_serve === true) selfBadge = '<span class="badge badge-self">Self-Serve</span>';
    
    let buildBadge = `<span class="badge badge-${{app.buildability_verdict}}">${{app.buildability_verdict}}</span>`;
    let confBadge = `<span class="badge badge-${{app.confidence || 'low'}}">${{app.confidence || 'low'}}</span>`;
    
    let ev = '—';
    if (app.evidence_urls && app.evidence_urls.length) {{
      ev = app.evidence_urls.slice(0,2).map(u => `<a href="${{u}}" target="_blank" class="evidence-link">📄</a>`).join(' ');
    }}
    
    tr.innerHTML = `
      <td><strong>${{app.name}}</strong></td>
      <td>${{app.category || ''}}</td>
      <td>${{authStr}}</td>
      <td>${{selfBadge}}</td>
      <td>${{app.api_surface || 'unknown'}}</td>
      <td>${{buildBadge}}</td>
      <td>${{confBadge}}</td>
      <td>${{ev}}</td>
    `;
    tbody.appendChild(tr);
  }});
}}

function filterTable() {{
  const q = document.getElementById('searchInput').value.toLowerCase();
  const filtered = appData.filter(app =>
    app.name.toLowerCase().includes(q) ||
    (app.category || '').toLowerCase().includes(q) ||
    (app.auth_methods || []).join(' ').toLowerCase().includes(q) ||
    (app.api_surface || '').toLowerCase().includes(q)
  );
  renderTable(filtered);
}}

let sortDirection = {{}};
function sortTable(col) {{
  const keyMap = ['name', 'category', 'auth_methods', 'self_serve', 'api_surface', 'buildability_verdict', 'confidence'];
  const key = keyMap[col];
  const dir = sortDirection[col] === 'asc' ? -1 : 1;
  sortDirection[col] = dir === 1 ? 'asc' : 'desc';
  const sorted = [...appData].sort((a, b) => {{
    let va = a[key] ?? '';
    let vb = b[key] ?? '';
    if (Array.isArray(va)) va = va.join(',').toLowerCase();
    else va = String(va).toLowerCase();
    if (Array.isArray(vb)) vb = vb.join(',').toLowerCase();
    else vb = String(vb).toLowerCase();
    return va.localeCompare(vb) * dir;
  }});
  renderTable(sorted);
}}

// Initial render
renderTable(appData);
</script>

</body>
</html>"""

# Replace placeholders
html = html_template.format(
    today=today,
    headlines_html=headlines_html,
    app_data=app_data_json
)

# Write with UTF-8 encoding to support emoji
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html generated! Open it in your browser.")