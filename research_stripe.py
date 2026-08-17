from web_researcher import research_app
import json
import os
from dotenv import load_dotenv

load_dotenv()

parsed, raw = research_app(
    None,
    "Stripe",
    "stripe.com/docs/api",
    "Finance and Fintech"
)

print("=== PARSED ===")
print(json.dumps(parsed, indent=2) if parsed else None)
print()
print("=== RAW (first 500 chars) ===")
print(raw[:500] if raw else None)