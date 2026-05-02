import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.db import engine, get_session
from app.models import Listing
from app.schemas import ListingCreate
from app.services import llm_service

router = APIRouter(prefix="/listings", tags=["listings"])


def _extract_features_bg(listing_id: str) -> None:
    with Session(engine) as session:
        listing = session.get(Listing, listing_id)
        if not listing:
            return
        features = llm_service.extract_listing_features(listing)
        listing.extracted_features = json.dumps(features)
        session.add(listing)
        session.commit()


@router.post("", status_code=201)
def upsert_listing(
    body: ListingCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    existing = session.exec(
        select(Listing).where(Listing.external_id == body.external_id)
    ).first()

    raw_str = json.dumps(body.raw)

    if existing:
        existing.url = body.url
        existing.title = body.title
        existing.description = body.description
        existing.price = body.price
        existing.location = body.location
        existing.listing_type = body.listing_type
        existing.raw = raw_str
        session.add(existing)
        session.commit()
        session.refresh(existing)
        listing = existing
    else:
        listing = Listing(
            external_id=body.external_id,
            url=body.url,
            title=body.title,
            description=body.description,
            price=body.price,
            location=body.location,
            listing_type=body.listing_type,
            raw=raw_str,
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)

    background_tasks.add_task(_extract_features_bg, listing.id)
    return listing


@router.get("/{listing_id}")
def get_listing(listing_id: str, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
