"""
agent.py – orchestrator using Composio catalog + web research via Gemini.
"""

import argparse
import json
import os
import sys
import time
from dotenv import load_dotenv
from pydantic import ValidationError

from composio_lookup import lookup_toolkit
from schema import AppResearch
from web_researcher import research_app

try:
    from composio import Composio
except ImportError:
    Composio = None


def load_apps(limit: int | None = None) -> list[dict]:
    with open("data/apps.json") as f:
        apps = json.load(f)
    return apps[:limit] if limit else apps


def process_one_app(composio_client, composio_session, app: dict) -> dict:
    """
    Returns a dict with keys: 'result' (validated AppResearch dict, or
    None on failure) and 'status' ('ok' | 'validation_failed' | 'error'),
    plus 'note' with details for the failure log.
    """
    name = app["name"]

    # Tier 1: Composio catalog check
    composio_hit = None
    if composio_client is not None:
        try:
            composio_hit = lookup_toolkit(composio_client, name)
        except Exception as e:
            print(f"  [warn] Composio lookup errored for {name}: {e}")

    # Tier 2: web research using Composio session + Gemini
    try:
        parsed, raw_text = research_app(
            composio_session, name, app["website_hint"], app["category"]
        )
    except Exception as e:
        return {"result": None, "status": "error", "note": f"research_app raised: {e}"}

    if parsed is None:
        return {
            "result": None,
            "status": "error",
            "note": f"Could not parse model output. Raw: {raw_text[:300]}",
        }

    # Merge: Composio ground truth wins for auth‑related fields
    merged = dict(parsed)
    merged["app_id"] = app["app_id"]
    merged["name"] = name
    merged["category"] = app["category"]
    merged["website_hint"] = app["website_hint"]

    if composio_hit and composio_hit.get("found"):
        merged["composio_toolkit_exists"] = True
        merged["composio_auth_schemes"] = composio_hit.get("auth_schemes", [])
        if merged.get("buildability_verdict") == "no":
            merged["buildability_verdict"] = "yes"
            merged["blocker"] = None
    else:
        merged["composio_toolkit_exists"] = False
        merged.setdefault("composio_auth_schemes", [])

    try:
        validated = AppResearch(**merged)
        return {"result": validated.model_dump(), "status": "ok", "note": ""}
    except ValidationError as e:
        return {
            "result": None,
            "status": "validation_failed",
            "note": f"Schema validation failed: {e}",
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N apps")
    parser.add_argument("--out", default="output/pass_1.json", help="Output file path")
    args = parser.parse_args()

    load_dotenv()
    composio_key = os.getenv("COMPOSIO_API_KEY")
    if not composio_key:
        sys.exit("COMPOSIO_API_KEY not set in .env")

    composio_client = Composio(api_key=composio_key)
    composio_session = composio_client.create(user_id="research_agent_dev")

    apps = load_apps(args.limit)
    print(f"Processing {len(apps)} app(s)...")

    results = []
    failures = []

    for i, app in enumerate(apps, 1):
        print(f"[{i}/{len(apps)}] {app['name']}...", end=" ", flush=True)
        outcome = process_one_app(composio_client, composio_session, app)

        if outcome["status"] == "ok":
            results.append(outcome["result"])
            print("done")
        else:
            failures.append({"app": app["name"], "status": outcome["status"], "note": outcome["note"]})
            print(f"FAILED ({outcome['status']})")

        time.sleep(1)  # rate‑limit courtesy

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)

    failures_path = args.out.replace(".json", "_failures.json")
    with open(failures_path, "w") as f:
        json.dump(failures, f, indent=2)

    print(f"\nDone. {len(results)} succeeded, {len(failures)} failed.")
    print(f"Results:  {args.out}")
    if failures:
        print(f"Failures: {failures_path}  (review these manually)")


if __name__ == "__main__":
    main()