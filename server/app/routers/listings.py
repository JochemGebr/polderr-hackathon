from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature
from app.schemas import ListingCreate

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("", status_code=201)
def upsert_listing(body: ListingCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Listing).where(Listing.external_id == body.external_id)
    ).first()

    if existing:
        existing.url = body.url
        existing.title = body.title
        existing.description = body.description
        existing.price = body.price
        existing.location = body.location
        existing.listing_type = body.listing_type
        existing.accepted_person_id = body.accepted_person_id
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    listing = Listing(
        external_id=body.external_id,
        url=body.url,
        title=body.title,
        description=body.description,
        price=body.price,
        location=body.location,
        listing_type=body.listing_type,
        accepted_person_id=body.accepted_person_id,
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


@router.get("/{listing_id}")
def get_listing(listing_id: str, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.post("/{listing_id}/features/{feature_id}", status_code=201)
def tag_feature(listing_id: str, feature_id: str, session: Session = Depends(get_session)):
    if not session.get(Listing, listing_id):
        raise HTTPException(status_code=404, detail="Listing not found")
    if not session.get(Feature, feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")

    existing = session.get(ListingFeature, (listing_id, feature_id))
    if existing:
        return existing

    tag = ListingFeature(listing_id=listing_id, feature_id=feature_id)
    session.add(tag)
    session.commit()
    return tag


@router.delete("/{listing_id}/features/{feature_id}", status_code=204)
def untag_feature(listing_id: str, feature_id: str, session: Session = Depends(get_session)):
    tag = session.get(ListingFeature, (listing_id, feature_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
