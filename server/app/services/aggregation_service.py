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

    # Look up descriptions for counted features
    def _with_desc(counter: Counter[str]) -> list[dict[str, Any]]:
        result = []
        for name, count in counter.most_common():
            feat = session.exec(select(Feature).where(Feature.name == name)).first()
            result.append({
                "name": name,
                "count": count,
                "description": feat.description if feat else None,
            })
        return result

    return {
        "listing_features": listing_features,
        "user_features": user_features,
        "accepted_features": _with_desc(accepted_counter),
        "rejected_features": _with_desc(rejected_counter),
    }


def compute_match(
    insights: dict[str, Any],
) -> tuple[float, list[dict[str, Any]], list[dict[str, Any]]]:
    user_names = {f["name"] for f in insights["user_features"]}
    accepted = insights["accepted_features"]  # [{name, count, description}]
    accepted_names = {f["name"] for f in accepted}
    accepted_map = {f["name"]: f for f in accepted}
    user_feature_map = {f["name"]: f for f in insights["user_features"]}

    strengths = [
        {"name": n, "description": user_feature_map[n].get("description", "")}
        for n in sorted(user_names & accepted_names,
                        key=lambda n: -accepted_map[n]["count"])
    ]

    weaknesses = [
        {"name": f["name"], "description": f.get("description", "")}
        for f in sorted(accepted, key=lambda f: -f["count"])
        if f["name"] not in user_names
    ]

    total_weight = sum(f["count"] for f in accepted)
    if total_weight > 0:
        strength_weight = sum(
            accepted_map[n]["count"] for n in user_names & accepted_names
        )
        score = round(strength_weight / total_weight, 3)
    else:
        # Cold-start: listing-feature × user-feature dot product
        lf_map = {f["name"]: f["score"] for f in insights["listing_features"]}
        total = sum(lf_map.values()) or 1
        matched = sum(
            lf_map.get(f["name"], 0) * f["score"]
            for f in insights["user_features"]
        )
        score = round(min(matched / total, 1.0), 3)

    return score, strengths, weaknesses


def get_principles() -> str:
    try:
        return PRINCIPLES_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
