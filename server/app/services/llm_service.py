import json
import os
import re
from typing import Any

import httpx
from sqlmodel import Session, select

from app.models import Feature, Listing, User

GEMMA_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemma-4-31b-it:generateContent"
)

LandlordFeatures = dict[str, float]


def _gemma(prompt: str) -> str:
    api_key = os.environ["GOOGLE_AI_API_KEY"]
    response = httpx.post(
        GEMMA_API_URL,
        params={"key": api_key},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
        },
        timeout=60.0,
    )
    response.raise_for_status()
    parts = response.json()["candidates"][0]["content"]["parts"]
    return parts[-1]["text"]


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s*```$", "", text).strip()


def extract_landlord_features(
    text: str, session: Session
) -> LandlordFeatures:
    existing = session.exec(select(Feature)).all()
    existing_keys = [f.name for f in existing]

    keys_section = (
        "\nPrefer reusing these existing keys over inventing synonyms:\n"
        + ", ".join(existing_keys)
        + "\n"
        if existing_keys
        else ""
    )

    prompt = (
        "You are analyzing a rental applicant's text to identify traits\n"
        "that landlords typically care about, or you are processing a rental"
        " description\nfor the same kind of traits.\n\n"
        "Extract key-value pairs where:\n"
        '- The key is a landlord concern (e.g. "cleanliness", "noise_level",\n'
        '  "party_behavior", "pet_ownership", "smoking",'
        ' "payment_reliability",\n'
        '  "stability", "social_activity", "is_female")\n'
        "- The value is a float between -1.0 and 1.0 indicating how strongly"
        " this trait\n  is suggested:\n"
        "  - 1.0 = very strong positive signal for landlord\n"
        "  - 0.0 = neutral or not mentioned\n"
        "  - -1.0 = very strong negative signal for landlord\n\n"
        "Only include traits that are actually evidenced in the text."
        " Use snake_case for keys."
        + keys_section
        + "\nRespond ONLY with valid JSON, no explanation, no code fences"
        " ```. Example:\n"
        '{"cleanliness": 0.8, "noise_level": -0.6, "party_behavior": -0.9}\n\n'
        "Text to analyze:\n" + text
    )

    features: dict[str, Any] = json.loads(_strip_fences(_gemma(prompt)))

    for key, value in features.items():
        if not isinstance(value, (int, float)) or not (-1 <= value <= 1):
            raise ValueError(f'Invalid value for feature "{key}": {value}')

    existing_key_set = set(existing_keys)
    for key in features:
        if key not in existing_key_set:
            session.add(Feature(name=key))
    session.commit()

    return {k: float(v) for k, v in features.items()}


def extract_listing_features(listing: Listing) -> list[dict[str, Any]]:
    """
    Analyse listing.description and return exactly 5 extracted features.

    Return format — list of 5 dicts:
    [
        {
            "name": str,          # snake_case identifier
            "description": str,   # one sentence explaining the signal
            "score": float,       # 0.0–1.0 relevance/confidence score
        },
        ...
    ]
    """
    # TODO: implement with your LLM of choice
    return [
        {
            "name": f"stub_feature_{i}",
            "description": "stub — implement extract_listing_features",
            "score": 0.0,
        }
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
      listing_features — the 5 extracted features with scores
    """
    # TODO: implement with your LLM of choice
    return (
        f"[stub] Motivation for {user.name or 'applicant'} "
        f"applying to '{listing.title}'."
        " Implement generate_motivation in llm_service.py."
    )
