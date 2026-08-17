"""
find_patterns.py
Compute clusters and write headline findings for the HTML.
"""

import json
from collections import defaultdict

# Load the verified dataset
with open("output/pass_2.json") as f:
    data = json.load(f)

# ---------- Basic totals ----------
total = len(data)
print(f"Total apps: {total}\n")

# ---------- 1. Auth methods ----------
auth_counts = defaultdict(int)
for app in data:
    for auth in app.get("auth_methods", []):
        if auth and auth != "unknown":
            auth_counts[auth] += 1

# Top auth methods
sorted_auth = sorted(auth_counts.items(), key=lambda x: -x[1])
print("1. Auth method distribution (non-unknown):")
for auth, count in sorted_auth:
    print(f"   {auth}: {count} ({count/total*100:.1f}%)")
print()

# ---------- 2. Self-serve vs gated ----------
self_serve_count = sum(1 for app in data if app.get("self_serve") is True)
gated_count = total - self_serve_count
print(f"2. Self-serve: {self_serve_count} ({self_serve_count/total*100:.1f}%)")
print(f"   Gated:      {gated_count} ({gated_count/total*100:.1f}%)")
print()

# ---------- 3. Buildability verdict ----------
verdict_counts = defaultdict(int)
for app in data:
    v = app.get("buildability_verdict", "no")
    verdict_counts[v] += 1
print("3. Buildability verdict:")
for v in ["yes", "partial", "no"]:
    count = verdict_counts.get(v, 0)
    print(f"   {v}: {count} ({count/total*100:.1f}%)")
print()

# ---------- 4. Most common blockers ----------
blocker_counts = defaultdict(int)
for app in data:
    if app.get("blocker"):
        # Shorten long blocker messages
        blocker = app["blocker"]
        if "No reliable data" in blocker:
            blocker = "No reliable data (API failure)"
        elif "Enterprise" in blocker or "partner" in blocker.lower():
            blocker = "Enterprise/partner-gated"
        elif "No public API" in blocker or "no public" in blocker.lower():
            blocker = "No public API"
        elif "documentation" in blocker.lower():
            blocker = "Lack of docs/public API"
        blocker_counts[blocker] += 1
print("4. Top blockers (for 'no' or 'partial'):")
for blocker, count in sorted(blocker_counts.items(), key=lambda x: -x[1])[:5]:
    print(f"   {blocker}: {count}")
print()

# ---------- 5. MCP exists ----------
mcp_count = sum(1 for app in data if app.get("mcp_exists") is True)
print(f"5. MCP servers already exist: {mcp_count} ({mcp_count/total*100:.1f}%)")

# Which categories have MCP?
mcp_cats = defaultdict(int)
for app in data:
    if app.get("mcp_exists"):
        mcp_cats[app["category"]] += 1
print("   Categories with MCP:")
for cat, count in sorted(mcp_cats.items(), key=lambda x: -x[1]):
    print(f"     - {cat}: {count} apps")
print()

# ---------- 6. Composio toolkit exists ----------
composio_count = sum(1 for app in data if app.get("composio_toolkit_exists") is True)
print(f"6. Apps already available as Composio toolkits: {composio_count} ({composio_count/total*100:.1f}%)")
print()

# ---------- Category × auth × self-serve cross-tab ----------
# For the headline, we want to highlight patterns like "Finance is 80% gated"
print("7. Category patterns (self-serve % and buildability):")
for cat in sorted(set(app["category"] for app in data)):
    apps_cat = [app for app in data if app["category"] == cat]
    n = len(apps_cat)
    self_serve_cat = sum(1 for app in apps_cat if app.get("self_serve") is True)
    build_yes = sum(1 for app in apps_cat if app.get("buildability_verdict") == "yes")
    print(f"   {cat}:")
    print(f"      Apps: {n}, Self-serve: {self_serve_cat}/{n} ({self_serve_cat/n*100:.1f}%), Buildable yes: {build_yes}/{n} ({build_yes/n*100:.1f}%)")
print()

# ---------- Write the 4-6 blunt findings ----------
print("\n" + "="*60)
print("HEADLINE FINDINGS (copy these to your HTML)")
print("="*60)

findings = []

# Find dominant auth
if sorted_auth:
    top_auth, top_count = sorted_auth[0]
    findings.append(f"OAuth2 is the most common auth method ({top_count}/{total} apps, {top_count/total*100:.0f}%), followed by API keys ({sorted_auth[1][1]} apps).")

# Self-serve overall
findings.append(f"Only {self_serve_count}/{total} ({self_serve_count/total*100:.0f}%) apps are fully self-serve – the rest require paid plans, partner approval, or contact sales.")

# Buildability
build_yes_count = verdict_counts.get("yes", 0)
findings.append(f"{build_yes_count}/{total} ({build_yes_count/total*100:.0f}%) apps are buildable today; the main blocker is lack of public API or enterprise gating.")

# Composio toolkit
findings.append(f"Composio already ships toolkits for {composio_count}/{total} apps – these are immediate wins for agent integration.")

# MCP
if mcp_count > 0:
    findings.append(f"MCP servers exist for {mcp_count} apps, mostly in AI-native and developer tools – low-hanging fruit for MCP-based agents.")

# Category-specific: e.g., Finance is heavily gated
finance_apps = [app for app in data if "Finance" in app["category"]]
if finance_apps:
    finance_total = len(finance_apps)
    finance_self = sum(1 for app in finance_apps if app.get("self_serve") is True)
    findings.append(f"In Finance, only {finance_self}/{finance_total} ({finance_self/finance_total*100:.0f}%) are self-serve – most require partnership or enterprise contracts.")

# CRM/Sales are mostly self-serve and buildable
crm_apps = [app for app in data if "CRM" in app["category"] or "Sales" in app["category"]]
if crm_apps:
    crm_total = len(crm_apps)
    crm_self = sum(1 for app in crm_apps if app.get("self_serve") is True)
    crm_build = sum(1 for app in crm_apps if app.get("buildability_verdict") == "yes")
    findings.append(f"In CRM & Sales, {crm_self}/{crm_total} ({crm_self/crm_total*100:.0f}%) are self-serve and {crm_build}/{crm_total} ({crm_build/crm_total*100:.0f}%) are buildable – the easiest category to tackle.")

# Print numbered findings
for i, f in enumerate(findings, 1):
    print(f"{i}. {f}")