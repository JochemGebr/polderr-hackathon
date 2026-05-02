from pathlib import Path
from typing import Any

from sqlmodel import Session, col, select

from app.models import Application, Listing

PRINCIPLES_PATH = Path(__file__).parent.parent.parent / "knowledge" / "principles.md"
TERMINAL_STATUSES = ["ACCEPTED", "REJECTED", "INVITED", "GHOSTED"]
PRICE_BAND_CENTS = 20_000  # ±€200


def find_similar_applications(
    session: Session,
    listing: Listing,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve past applications with completed outcomes that are similar to
    the given listing. Used as few-shot examples for the LLM recommendation.
    v1 uses SQL attribute filters — swap in vector similarity later if needed.
    """
    listing_query = select(Listing.id)
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


def get_principles() -> str:
    try:
        return PRINCIPLES_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
