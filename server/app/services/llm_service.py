from typing import Any

from app.models import Listing, User

# ── Interface contract for the LLM teammate ───────────────────────────────────
#
# extract_listing_features  →  identify 5 key features from the listing text
# generate_motivation       →  write a personalised application message
#
# Replace the stubs below with real LLM calls. No other files need changes.
# ─────────────────────────────────────────────────────────────────────────────


def extract_listing_features(listing: Listing) -> list[dict[str, Any]]:
    """
    Analyse listing.description and return exactly 5 extracted features.

    Return format — list of 5 dicts:
    [
        {
            "name": str,          # snake_case identifier, e.g. "prefers_quiet_tenant"
            "description": str,   # one sentence explaining what the landlord signals
            "score": float,       # 0.0–1.0 relevance/confidence score
        },
        ...
    ]

    Suggested prompt approach:
      - Ask the LLM to read the listing and identify the 5 most important signals
        a potential tenant should know about (requirements, preferences, dealbreakers)
      - Return structured JSON
    """
    # TODO: implement with your LLM of choice
    return [
        {"name": f"stub_feature_{i}", "description": "stub — implement extract_listing_features", "score": 0.0}
        for i in range(1, 6)
    ]


def generate_motivation(
    listing: Listing,
    user: User,
    listing_features: list[dict[str, Any]],
) -> str:
    """
    Write a personalised application motivation text.

    Inputs:
      listing          — title, description, location, price, listing_type
      user             — name, occupation, income, age, has_pets, bio, profile
      listing_features — the 5 extracted features with scores (from extract_listing_features)

    Suggested prompt approach:
      - System: you are helping a tenant write a compelling Kamernet application
      - Context: listing details + extracted feature signals
      - User profile: what makes this applicant a good match
      - Task: write a concise, personalised message in Dutch (or English) that addresses
        the landlord's signals and highlights the applicant's strengths

    Return: plain text string ready to send to the landlord.
    """
    # TODO: implement with your LLM of choice
    return (
        f"[stub] Motivation for {user.name or 'applicant'} "
        f"applying to '{listing.title}'. Implement generate_motivation in llm_service.py."
    )
