import json

# Load the JSON file
with open("output/pass_1.json") as f:
    data = json.load(f)

# List of apps to check
apps_to_check = ["Salesforce", "HubSpot", "Stripe", "Slack", "GitHub", "Notion"]

# Iterate and print details
for name in apps_to_check:
    app = next((x for x in data if x["name"] == name), None)
    if app:
        print(f"{name}:")
        print(f"  auth: {app.get('auth_methods')}")
        print(f"  self_serve: {app.get('self_serve')}")
        print(f"  api: {app.get('api_surface')}")
        print(f"  composio: {app.get('composio_toolkit_exists')} {app.get('composio_auth_schemes')}")
        print(f"  verdict: {app.get('buildability_verdict')}")
        print(f"  confidence: {app.get('confidence')}")
        print(f"  evidence: {app.get('evidence_urls')[:2]}")
        print()
