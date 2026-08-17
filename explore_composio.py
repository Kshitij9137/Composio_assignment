"""
explore_composio.py

Run this BEFORE trusting composio_lookup.py. Composio's SDK response
shapes can drift between versions, and I can't test against your live
account from here -- so this prints the raw response for a couple of
known toolkits (github, stripe) so you can see the actual field names
your SDK version returns, and adjust composio_lookup.py if anything
doesn't match.

Run with:  python explore_composio.py
"""

import json
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

for slug in ["github", "stripe", "slack"]:
    print(f"\n{'=' * 50}\ntoolkits.get('{slug}')\n{'=' * 50}")
    try:
        result = composio.toolkits.get(slug)
        # result is likely a pydantic model -- try the common ways to
        # turn it into plain JSON for inspection
        if hasattr(result, "model_dump"):
            print(json.dumps(result.model_dump(), indent=2, default=str))
        elif hasattr(result, "dict"):
            print(json.dumps(result.dict(), indent=2, default=str))
        else:
            print(result)
    except Exception as e:
        print(f"Lookup failed: {type(e).__name__}: {e}")

print(f"\n{'=' * 50}\ntoolkits.list() -- first few results\n{'=' * 50}")
try:
    listing = composio.toolkits.list()
    print(json.dumps(listing, indent=2, default=str)[:2000])
except Exception as e:
    print(f"List failed: {type(e).__name__}: {e}")

print(
    "\nLook at the printed fields above. In particular, check:\n"
    " - What key holds the auth scheme(s)? (assumed: composio_managed_auth_schemes)\n"
    " - What key confirms the toolkit is active? (assumed: enabled)\n"
    " - Does toolkits.list() accept a search/query param for fuzzy name matching?\n"
    "If any of these differ, update the field names in composio_lookup.py."
)
