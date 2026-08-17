"""
schema.py

This defines the exact "form" every app's research result must fill out.
Using pydantic means Python will automatically REJECT any data that doesn't
match this shape -- e.g. if the agent tries to save buildability_verdict
as "maybe", it will error instead of silently corrupting your dataset.

Beginner note: a "Literal" type means "must be exactly one of these strings" --
it's how we enforce the fixed vocabulary (rest/graphql/none/unknown, etc.)
so results can actually be clustered later, instead of every entry using
slightly different wording for the same idea.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


AuthMethod = Literal["oauth2", "api_key", "basic", "token", "other", "unknown"]
ApiSurface = Literal["rest", "graphql", "rest_and_graphql", "none", "unknown"]
BuildabilityVerdict = Literal["yes", "partial", "no"]
Confidence = Literal["high", "medium", "low"]


class AppResearch(BaseModel):
    app_id: int = Field(..., description="Matches the # from the source list, 1-100")
    name: str
    category: str
    website_hint: str

    one_liner: str = Field(..., description="What the app does, one sentence")

    auth_methods: List[AuthMethod] = Field(
        default_factory=list,
        description="Every auth method mentioned in the docs, can be more than one",
    )

    self_serve: bool = Field(
        ..., description="Can a developer get credentials themselves, free or on trial"
    )
    self_serve_basis: str = Field(
        ..., description="Why you concluded that -- your evidence, in your own words"
    )
    gating_reason: Optional[str] = Field(
        default=None, description="If not self-serve, what's blocking it"
    )

    api_surface: ApiSurface
    api_breadth_note: str = Field(
        default="", description="Roughly how broad the API is, in a phrase"
    )
    mcp_exists: bool = Field(default=False)
    mcp_note: Optional[str] = Field(default=None)

    buildability_verdict: BuildabilityVerdict
    blocker: Optional[str] = Field(
        default=None, description="Main blocker if verdict is not 'yes'"
    )

    # Ground-truth signal from Composio's own catalog, distinct from
    # mcp_exists (which is about third-party MCP servers found via research).
    # If Composio already ships this toolkit, that's strong evidence for
    # buildability and for the real auth scheme used in production.
    composio_toolkit_exists: bool = Field(default=False)
    composio_auth_schemes: List[str] = Field(default_factory=list)

    evidence_urls: List[str] = Field(
        default_factory=list, description="The actual docs pages used as evidence"
    )
    confidence: Confidence

    # Filled in during Phase 4 (verification), not during first research pass
    verified: bool = Field(default=False)
    verification_note: Optional[str] = Field(default=None)


if __name__ == "__main__":
    # Quick sanity check: this should print without errors.
    # Try changing "rest" to "restt" below to see pydantic reject bad data.
    example = AppResearch(
        app_id=81,
        name="Stripe",
        category="Finance and Fintech",
        website_hint="stripe.com/docs/api",
        one_liner="Payments, billing, and financial infrastructure API",
        auth_methods=["api_key"],
        self_serve=True,
        self_serve_basis="Dashboard signup gives instant test-mode API keys",
        api_surface="rest",
        api_breadth_note="Very broad -- payments, subscriptions, connect, invoicing",
        mcp_exists=False,
        buildability_verdict="yes",
        evidence_urls=["https://stripe.com/docs/api"],
        confidence="high",
        composio_toolkit_exists=True,
        composio_auth_schemes=["api_key"],
    )
    print("Schema OK. Example entry:")
    print(example.model_dump_json(indent=2))
