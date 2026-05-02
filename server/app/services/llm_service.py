import json
import os
import re
from typing import Any

import httpx
from sqlmodel import Session, select

from app.models import Feature, Listing, User, UserFeature

GEMMA_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta"
    "/models/gemma-4-31b-it:generateContent"
)

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


def _extract_features(
    text: str, session: Session
) -> list[dict[str, Any]]:
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
        "You are analyzing text about a rental listing or applicant to"
        " identify\ntraits that landlords typically care about.\n\n"
        "Return a JSON array where each object has:\n"
        '- "name": snake_case landlord concern'
        ' (e.g. "cleanliness", "noise_level",\n'
        '  "pet_ownership", "smoking", "payment_reliability",'
        ' "stability")\n'
        '- "description": one sentence explaining the signal in the text\n'
        '- "score": float 0.0–1.0 for how strongly this trait is'
        " evidenced\n\n"
        "Only include traits actually evidenced in the text."
        + keys_section
        + "\nRespond ONLY with a valid JSON array, no explanation."
        " Example:\n"
        '[{"name": "cleanliness", "description":'
        ' "Applicant mentions keeping spaces tidy.", "score": 0.8}]\n\n'
        "Text to analyze:\n" + text
    )

    raw: list[Any] = json.loads(_strip_fences(_gemma(prompt)))

    existing_key_set = {f.name for f in existing}
    result = []
    for item in raw:
        name = item["name"]
        score = float(item["score"])
        if not (0.0 <= score <= 1.0):
            raise ValueError(
                f'Score out of range for "{name}": {score}'
            )
        if name not in existing_key_set:
            session.add(Feature(
                name=name,
                description=item.get("description"),
            ))
            existing_key_set.add(name)
        result.append({
            "name": name,
            "description": item.get("description", ""),
            "score": score,
        })
    session.commit()

    return result


def _user_profile_text(user: User) -> str:
    parts = []
    if user.occupation:
        parts.append(f"Occupation: {user.occupation}")
    if user.income is not None:
        parts.append(f"Monthly income: €{user.income}")
    if user.age is not None:
        parts.append(f"Age: {user.age}")
    if user.gender:
        parts.append(f"Gender: {user.gender}")
    parts.append(f"Has pets: {'yes' if user.has_pets else 'no'}")
    if user.bio:
        parts.append(f"Bio: {user.bio}")
    return "\n".join(parts)


def extract_and_store_user_features(
    user: User, session: Session
) -> None:
    text = _user_profile_text(user)
    if not text.strip():
        return

    features = _extract_features(text, session)

    old = session.exec(
        select(UserFeature).where(UserFeature.user_id == user.user_id)
    ).all()
    for uf in old:
        session.delete(uf)
    session.flush()

    for item in features:
        feature = session.exec(
            select(Feature).where(Feature.name == item["name"])
        ).first()
        if feature:
            session.add(UserFeature(
                user_id=user.user_id,
                feature_id=feature.feature_id,
                score=item["score"],
            ))
    session.commit()


def extract_listing_features(
    listing: Listing, session: Session
) -> list[dict[str, Any]]:
    return _extract_features(listing.description, session)


def generate_motivation(
    listing: Listing,
    user: User,
    listing_features: list[dict[str, Any]],
    session: Session,
    strengths: list[dict[str, Any]] | None = None,
    weaknesses: list[dict[str, Any]] | None = None,
) -> str:
    from app.services.aggregation_service import (
        find_similar_applications,
        get_principles,
    )

    principles = get_principles()

    price_str = (
        f"€{listing.price // 100}/month" if listing.price else "not stated"
    )
    features_str = "\n".join(
        f"- {f['name']}: {f['description']} (score: {f['score']:.2f})"
        for f in listing_features
    ) or "none extracted"

    profile_lines = [
        f"Name: {user.name or 'not stated'}",
        f"Occupation: {user.occupation or 'not stated'}",
        f"Monthly income: "
        + (f"€{user.income}" if user.income else "not stated"),
        f"Age: {user.age or 'not stated'}",
        f"Gender: {user.gender or 'not stated'}",
        f"Has pets: {'yes' if user.has_pets else 'no'}",
    ]
    if user.bio:
        profile_lines.append(f"Bio: {user.bio}")
    profile_str = "\n".join(profile_lines)

    similar = find_similar_applications(session, listing)
    examples_str = ""
    if similar:
        parts = []
        for ex in similar:
            part = (
                f"Outcome: {ex['outcome']}\n"
                f"Occupation: {ex['user_occupation'] or '?'}, "
                f"Income: {ex['user_income'] or '?'}, "
                f"Pets: {'yes' if ex['user_has_pets'] else 'no'}\n"
                f"Message: {ex['message_sent'] or '(none)'}"
            )
            if ex["result_notes"]:
                part += f"\nNotes: {ex['result_notes']}"
            parts.append(part)
        examples_str = "\n\n---\n\n".join(parts)

    fit_str = ""
    if strengths or weaknesses:
        fit_lines = []
        if strengths:
            fit_lines.append(
                "Strengths to highlight (traits that got similar applicants accepted): "
                + ", ".join(s["name"] for s in strengths)
            )
        if weaknesses:
            fit_lines.append(
                "Gaps vs accepted applicants (traits they had that this applicant lacks): "
                + ", ".join(w["name"] for w in weaknesses)
            )
        fit_str = "\n".join(fit_lines)

    prompt = (
        "You are writing a rental application motivation letter"
        " on behalf of a tenant.\n"
        "Write 150–250 words. Use the language of the listing"
        " description.\n"
        "Address the landlord's concerns directly."
        " Reference specific listing details.\n"
        "State income clearly. Never use generic openers.\n"
        "Return only the letter text — no subject line,"
        " no labels, no formatting.\n\n"
        + (f"## Principles\n{principles}\n\n" if principles else "")
        + f"## Listing\n"
        f"Title: {listing.title}\n"
        f"Location: {listing.location or 'not stated'}\n"
        f"Price: {price_str}\n"
        f"Description: {listing.description}\n\n"
        f"## What the landlord cares about\n{features_str}\n\n"
        f"## Applicant profile\n{profile_str}\n\n"
        + (f"## Applicant fit (from crowdsourced outcomes)\n{fit_str}\n\n" if fit_str else "")
        + (
            f"## Similar past applications\n{examples_str}\n\n"
            if examples_str
            else ""
        )
        + "## Letter"
    )

    return _gemma(prompt)
