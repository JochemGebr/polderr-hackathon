from typing import Any

from app.models import Listing, User

# ── Interface contract for the LLM teammate ──────────────────────────────────
#
# extract_listing_features: parse a listing into structured signals
# generate_recommendation:  produce a personalised application message
#
# Both functions receive everything they need. Implement by replacing the stubs
# below with real LLM calls (Claude, OpenAI, etc.). No other files need changes.
# ─────────────────────────────────────────────────────────────────────────────


def extract_listing_features(listing: Listing) -> dict[str, Any]:
    """
    Parse listing.description (and listing.raw) and return structured signals.

    Expected output shape:
    {
        "highlights": list[str],       # things landlord emphasises positively
        "dealbreakers": list[str],     # hard requirements (no pets, no students…)
        "preferred_profile": list[str],# what kind of tenant they're looking for
        "landlord_tone": str,          # "formal" | "casual" | "corporate"
        "required_income_multiplier": float | None,  # e.g. 3.0 = 3× rent
    }
    """
    # TODO: implement with your LLM of choice
    return {
        "highlights": [],
        "dealbreakers": [],
        "preferred_profile": [],
        "landlord_tone": "formal",
        "required_income_multiplier": None,
    }


def generate_recommendation(
    listing: Listing,
    user: User,
    similar_applications: list[dict[str, Any]],
    principles: str,
) -> dict[str, Any]:
    """
    Write a personalised application message and surface key talking points.

    Inputs:
      listing               — the target listing (description, features, raw)
      user                  — the applicant's profile (bio, income, occupation…)
      similar_applications  — past application-outcome pairs for few-shot context
      principles            — contents of knowledge/principles.md (stable rules)

    Expected output shape:
    {
        "message": str,              # ready-to-send application text
        "key_strengths": list[str],  # user strengths to highlight
        "addressed_concerns": list[str],  # landlord concerns the message tackles
    }
    """
    # TODO: implement with your LLM of choice
    # Suggested prompt structure:
    #   1. System: role + principles doc
    #   2. Few-shot: similar_applications examples with outcome labels
    #   3. User turn: listing description + extracted_features + user profile
    return {
        "message": f"[stub] Personalised message for {user.name or 'applicant'} → {listing.title}",
        "key_strengths": ["fill in after LLM integration"],
        "addressed_concerns": [],
    }
