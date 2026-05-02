from collections import Counter
from pathlib import Path
from typing import Any

from sqlmodel import Session, col, select

from app.models import (
    Application,
    Feature,
    Listing,
    ListingFeature,
    PersonFeature,
    User,
    UserFeature,
)

PRINCIPLES_PATH = Path(__file__).parent.parent.parent / "knowledge" / "principles.md"
TERMINAL_STATUSES = ["ACCEPTED", "REJECTED", "INVITED", "GHOSTED"]
PRICE_BAND_CENTS = 20_000  # ±€200


def find_similar_applications(
    session: Session,
    listing: Listing,
    limit: int = 5,
) -> list[dict[str, Any]]:
    listing_query = select(Listing.listing_id)
    if listing.listing_type:
        listing_query = listing_query.where(Listing.listing_type == listing.listing_type)
    if listing.location:
        listing_query = listing_query.where(Listing.location == listing.location)
    if listing.price is not None:
        listing_query = listing_query.where(Listing.price >= listing.price - PRICE_BAND_CENTS)
        listing_query = listing_query.where(Listing.price <= listing.price + PRICE_BAND_CENTS)

    matching_ids = session.exec(listing_query).all()
    if not matching_ids:
        return []

    applications = session.exec(
        select(Application)
        .where(col(Application.status).in_(TERMINAL_STATUSES))
        .where(col(Application.listing_id).in_(matching_ids))
        .order_by(Application.applied_at.desc())
        .limit(limit)
    ).all()

    return [
        {
            "outcome": app.status,
            "result_notes": app.result_notes,
            "listing_title": app.listing.title if app.listing else "",
            "listing_description": app.listing.description if app.listing else "",
            "user_occupation": app.user.occupation if app.user else None,
            "user_income": app.user.income if app.user else None,
            "user_has_pets": app.user.has_pets if app.user else False,
            "message_sent": app.message,
        }
        for app in applications
    ]


def get_insights(
    session: Session,
    listing: Listing,
    user: User,
) -> dict[str, Any]:
    # ── 1. Current listing features ──────────────────────────────────────────
    listing_tags = session.exec(
        select(ListingFeature).where(ListingFeature.listing_id == listing.listing_id)
    ).all()
    listing_feature_ids = [t.feature_id for t in listing_tags]
    listing_features = []
    for tag in listing_tags:
        feature = session.get(Feature, tag.feature_id)
        if feature:
            listing_features.append({
                "name": feature.name,
                "description": feature.description,
                "score": tag.score,
            })

    # ── 2. Similar listings by feature overlap ────────────────────────────────
    similar_listing_ids: list[str] = []
    if listing_feature_ids:
        similar_tags = session.exec(
            select(ListingFeature)
            .where(col(ListingFeature.feature_id).in_(listing_feature_ids))
            .where(ListingFeature.listing_id != listing.listing_id)
        ).all()
        similar_listing_ids = list({t.listing_id for t in similar_tags})

    # ── 3. Accepted / rejected feature counts from similar listings ──────────
    accepted_counter: Counter[str] = Counter()
    rejected_counter: Counter[str] = Counter()

    if similar_listing_ids:
        for status, counter in (
            ("ACCEPTED", accepted_counter),
            ("REJECTED", rejected_counter),
        ):
            apps = session.exec(
                select(Application)
                .where(Application.status == status)
                .where(col(Application.listing_id).in_(similar_listing_ids))
            ).all()
            for app in apps:
                # In seeded data app.user_id == person_id
                person_tags = session.exec(
                    select(PersonFeature).where(PersonFeature.person_id == app.user_id)
                ).all()
                for pt in person_tags:
                    feature = session.get(Feature, pt.feature_id)
                    if feature:
                        counter[feature.name] += 1

    # ── 4. Current user features ──────────────────────────────────────────────
    user_tags = session.exec(
        select(UserFeature).where(UserFeature.user_id == user.user_id)
    ).all()
    user_features = []
    for tag in user_tags:
        feature = session.get(Feature, tag.feature_id)
        if feature:
            user_features.append({
                "name": feature.name,
                "description": feature.description,
                "score": tag.score,
            })

    return {
        "listing_features": listing_features,
        "user_features": user_features,
        "accepted_features": [
            {"name": n, "count": c} for n, c in accepted_counter.most_common()
        ],
        "rejected_features": [
            {"name": n, "count": c} for n, c in rejected_counter.most_common()
        ],
    }


def get_principles() -> str:
    try:
        return PRINCIPLES_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
