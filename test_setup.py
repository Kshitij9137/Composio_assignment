"""
test_setup.py

Run this once after signing up for Composio and filling in .env.
It does nothing "real" yet -- it just proves your API key works and that
you can create a session and list some available tools. This is the
"hello world" checkpoint before you write any research logic.

Run with:  python test_setup.py
"""

import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
if not api_key:
    raise SystemExit(
        "COMPOSIO_API_KEY not set. Copy .env.example to .env and fill it in."
    )

composio = Composio(api_key=api_key)

# A session is Composio's unit of "an agent acting on behalf of one user".
# For this project there's no real end-user -- we're the only user -- so
# any stable string works as the user_id. Using the same one every run
# lets Composio reuse auth/connections instead of creating new ones.
session = composio.create(user_id="research_agent_dev")

print("Connected to Composio.")
print("Session ID:", session.session_id)

# session.tools() returns a small set of *meta* tools (search, connect,
# execute) rather than loading thousands of app-specific tool schemas --
# that's what we'll hand to the LLM in Phase 2 to let it search the web
# and fetch docs pages for each app.
tools = session.tools()
print(f"Session has {len(tools)} meta tool(s) available:")
for t in tools:
    name = t.get("function", {}).get("name", t.get("name", "unknown"))
    print(" -", name)

print("\nSetup looks good. You're ready for Phase 2 (the research agent).")
