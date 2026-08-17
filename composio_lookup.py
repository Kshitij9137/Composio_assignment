"""
composio_lookup.py

Tier 1 of the research pipeline: before asking an LLM to guess anything,
check whether Composio already ships a toolkit for this app. If it does,
we get REAL production auth-scheme data straight from Composio's own
catalog -- no inference needed, and it's automatic proof of buildability
(they already built it).

IMPORTANT: run explore_composio.py first and confirm the field names
below (enabled, composio_managed_auth_schemes) match what your SDK
version actually returns. Adjust if they don't.
"""

import re
from typing import Optional, Dict, Any


def _slug_candidates(app_name: str) -> list[str]:
    """
    Composio toolkit slugs are typically the app name, lowercased, with
    spaces removed (e.g. "Google Ads" -> "googleads"). We don't know the
    exact convention for every app, so we try a few reasonable variants
    in order, most-likely-first.
    """
    base = re.sub(r"[^a-zA-Z0-9 ]", "", app_name).strip().lower()
    no_space = base.replace(" ", "")
    underscored = base.replace(" ", "_")
    hyphenated = base.replace(" ", "-")
    first_word = base.split(" ")[0] if " " in base else base

    # dict.fromkeys() dedupes while preserving order (first match wins)
    return list(dict.fromkeys([no_space, underscored, hyphenated, first_word]))


def lookup_toolkit(composio, app_name: str) -> Optional[Dict[str, Any]]:
    """
    Returns a normalized dict if Composio has this toolkit, else None.
    Tries direct slug lookups first (cheap, exact), then falls back to
    a client-side search over toolkits.list() if the direct lookups fail.
    """
    for slug in _slug_candidates(app_name):
        try:
            result = composio.toolkits.get(slug)
            return _normalize(result, matched_via=f"direct slug '{slug}'")
        except Exception:
            continue  # this slug guess was wrong, try the next one

    # Fallback: list all toolkits and look for a name match. Wrapped in
    # try/except because list() signature/pagination may vary by version --
    # see explore_composio.py output before relying on this path.
    try:
        listing = composio.toolkits.list()
        items = getattr(listing, "items", listing)  # handle both shapes
        for item in items:
            name = getattr(item, "name", None) or item.get("name", "")
            if name.strip().lower() == app_name.strip().lower():
                slug = getattr(item, "slug", None) or item.get("slug")
                result = composio.toolkits.get(slug)
                return _normalize(result, matched_via="list search")
    except Exception:
        pass

    return None


def _normalize(result, matched_via: str) -> Dict[str, Any]:
    """Turn whatever object type Composio returns into a plain dict."""
    if hasattr(result, "model_dump"):
        data = result.model_dump()
    elif hasattr(result, "dict"):
        data = result.dict()
    elif isinstance(result, dict):
        data = result
    else:
        data = {"raw": str(result)}

    return {
        "found": True,
        "matched_via": matched_via,
        "enabled": data.get("enabled", True),
        "auth_schemes": data.get("composio_managed_auth_schemes", []),
        "slug": data.get("slug"),
        "raw": data,  # kept for debugging, not written to the final schema
    }


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from composio import Composio

    load_dotenv()
    composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

    # Quick manual test across a few apps from the list -- one that should
    # definitely exist (GitHub), one obscure one that probably doesn't.
    for name in ["GitHub", "Stripe", "fanbasis", "Waterfall.io"]:
        result = lookup_toolkit(composio, name)
        print(f"{name}: {result if result else 'not found in Composio catalog'}")
