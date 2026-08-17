"""
web_researcher.py – uses Gemini with retries and fallback.
"""

import json
import re
import os
import time
from typing import Optional, Tuple

from google import genai
from google.genai import types

# ----- Configuration -----
GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-1.5-flash",
    "gemini-1.5-pro",          # more reliable, slower
    "gemini-flash-latest",
]

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds (doubles each retry)

SYSTEM_PROMPT = """You are a research agent investigating a SaaS app's developer/API surface for a technical due-diligence report.

Use your knowledge and the given app name, category, and website hint to answer.
Never invent facts; if uncertain, set confidence to "low".

Respond with ONLY a single JSON object, no prose, no markdown fences. Use exactly these keys:

{
  "one_liner": "string, what the app does, one sentence",
  "auth_methods": ["oauth2" | "api_key" | "basic" | "token" | "other" | "unknown"],
  "self_serve": true | false,
  "self_serve_basis": "string, your evidence for the self_serve determination",
  "gating_reason": "string or null, only if self_serve is false",
  "api_surface": "rest" | "graphql" | "rest_and_graphql" | "none" | "unknown",
  "api_breadth_note": "string, roughly how broad the API is",
  "mcp_exists": true | false,
  "mcp_note": "string or null",
  "buildability_verdict": "yes" | "partial" | "no",
  "blocker": "string or null, only if verdict is not yes",
  "evidence_urls": ["url", ...],
  "confidence": "high" | "medium" | "low"
}
"""

def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    return json.loads(cleaned)

def _default_response(app_name: str, website_hint: str) -> dict:
    """Fallback when Gemini fails after all retries."""
    return {
        "one_liner": f"Unable to research – please verify manually",
        "auth_methods": ["unknown"],
        "self_serve": False,
        "self_serve_basis": "Gemini API unavailable after retries. Manual verification needed.",
        "gating_reason": "Unknown due to API failure",
        "api_surface": "unknown",
        "api_breadth_note": "",
        "mcp_exists": False,
        "mcp_note": None,
        "buildability_verdict": "no",
        "blocker": "No reliable data obtained",
        "evidence_urls": [website_hint] if website_hint else [],
        "confidence": "low",
    }

def research_app(
    session,               # unused, kept for compatibility
    app_name: str,
    website_hint: str,
    category: str,
) -> Tuple[Optional[dict], str]:
    """
    Uses Gemini to fill the schema, with retries.
    Returns (parsed_dict or default_fallback, raw_text)
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    user_prompt = (
        f"App: {app_name}\n"
        f"Category: {category}\n"
        f"Website / hint: {website_hint}\n\n"
        f"Based on your knowledge and the hint, fill the JSON object."
    )

    last_error = None
    for attempt in range(MAX_RETRIES):
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.1,
                        max_output_tokens=1500,
                        response_mime_type="application/json",
                    ),
                )
                full_text = response.text
                parsed = _extract_json(full_text)
                # Ensure evidence_urls
                if not parsed.get("evidence_urls") and website_hint:
                    parsed["evidence_urls"] = [
                        f"https://{website_hint}" if not website_hint.startswith("http") else website_hint
                    ]
                return parsed, full_text
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error:
                    # retry after delay
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                    break  # try next model? Actually we break out of model loop to retry entire list
                # other errors: continue to next model
                continue
        else:
            # all models failed without 503? break retry loop
            break

    # All attempts failed – return fallback
    fallback = _default_response(app_name, website_hint)
    return fallback, f"Gemini failed after {MAX_RETRIES} attempts. Last error: {last_error}"

# ----- Smoke test (run this file directly) -----
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    parsed, raw = research_app(
        None,
        "Waterfall.io",
        "waterfall.io (contact/company intel)",
        "Data, SEO and Scraping"
    )
    if parsed:
        print("✅ Parsed successfully:")
        print(json.dumps(parsed, indent=2))
    else:
        print("❌ Failed to parse. Raw output:")
        print(raw)