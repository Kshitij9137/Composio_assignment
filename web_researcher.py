"""
web_researcher.py – uses Gemini with a strict JSON prompt.
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
    "gemini-3.5-flash",        # Top choice – speed & accuracy
    "gemini-2.5-flash",        # Stable fallback
    "gemini-3.1-flash-lite",   # Cost‑optimised
    "gemini-2.5-flash-lite",   # Cheapest fallback
]

MAX_RETRIES = 2
RETRY_DELAY = 2

def _extract_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    return json.loads(cleaned)

def research_app(
    session,  # unused
    app_name: str,
    website_hint: str,
    category: str,
) -> Tuple[Optional[dict], str]:
    """
    Uses Gemini to research the app and return structured JSON.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "GEMINI_API_KEY not set in .env"

    client = genai.Client(api_key=api_key)

    # Build a very explicit prompt
    prompt = f"""You are a researcher. Research the app "{app_name}" (category: {category}, website hint: {website_hint}).

Return a valid JSON object with these exact keys. Use your knowledge about this app. If unsure, set confidence to "low" and explain why.

Keys:
- one_liner: string, what the app does in one sentence
- auth_methods: list of strings, choose from ["oauth2","api_key","basic","token","other","unknown"]
- self_serve: boolean, can a developer sign up for free and get API keys instantly?
- self_serve_basis: string, your reasoning/evidence for self_serve
- gating_reason: string or null, only if self_serve is false
- api_surface: string, choose from ["rest","graphql","rest_and_graphql","none","unknown"]
- api_breadth_note: string, roughly how broad the API is
- mcp_exists: boolean, is there an existing MCP server?
- mcp_note: string or null
- buildability_verdict: string, choose from ["yes","partial","no"]
- blocker: string or null, only if verdict is not yes
- evidence_urls: list of strings, URLs of documentation (at least use the website hint)
- confidence: string, choose from ["high","medium","low"]

Example for Stripe:
{{
  "one_liner": "Payments, billing, and financial infrastructure API",
  "auth_methods": ["api_key"],
  "self_serve": true,
  "self_serve_basis": "Anyone can sign up and get test API keys immediately",
  "gating_reason": null,
  "api_surface": "rest",
  "api_breadth_note": "Very broad – payments, subscriptions, connect, invoicing",
  "mcp_exists": false,
  "mcp_note": null,
  "buildability_verdict": "yes",
  "blocker": null,
  "evidence_urls": ["https://stripe.com/docs/api"],
  "confidence": "high"
}}

Now return ONLY the JSON for {app_name}. No extra text.
"""

    last_error = None
    for attempt in range(MAX_RETRIES):
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=1500,
                        response_mime_type="application/json",
                    ),
                )
                full_text = response.text
                parsed = _extract_json(full_text)
                
                # Ensure evidence_urls has at least the hint
                if not parsed.get("evidence_urls") and website_hint:
                    if not website_hint.startswith("http"):
                        parsed["evidence_urls"] = [f"https://{website_hint}"]
                    else:
                        parsed["evidence_urls"] = [website_hint]
                
                return parsed, full_text
                
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error:
                    time.sleep(RETRY_DELAY * (2 ** attempt))
                    break
                continue
    
    # Fallback: return a low-confidence default
    fallback = {
        "one_liner": f"Could not research {app_name} – API unavailable",
        "auth_methods": ["unknown"],
        "self_serve": False,
        "self_serve_basis": f"Gemini API failed: {last_error}",
        "gating_reason": "Unable to verify due to API error",
        "api_surface": "unknown",
        "api_breadth_note": "",
        "mcp_exists": False,
        "mcp_note": None,
        "buildability_verdict": "no",
        "blocker": "No reliable data obtained",
        "evidence_urls": [website_hint] if website_hint else [],
        "confidence": "low",
    }
    return fallback, f"Fallback used. Last error: {last_error}"