import json

data = json.load(open("output/pass_1.json"))
print(f"Total apps: {len(data)}")
print(f"High confidence: {sum(1 for x in data if x.get('confidence')=='high')}")
print(f"Medium: {sum(1 for x in data if x.get('confidence')=='medium')}")
print(f"Low: {sum(1 for x in data if x.get('confidence')=='low')}")
print(f"Self-serve True: {sum(1 for x in data if x.get('self_serve') is True)}")
print(f"Composio toolkit exists: {sum(1 for x in data if x.get('composio_toolkit_exists'))}")
print()
print("Sample of first 3 apps:")
for app in data[:3]:
    print(f"- {app['name']}: auth={app.get('auth_methods')}, self_serve={app.get('self_serve')}, verdict={app.get('buildability_verdict')}, conf={app.get('confidence')}")
