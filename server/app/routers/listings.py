from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature
from app.schemas import ExtractedFeature, ListingCreate, ListingResponse
from app.services import llm_service

router = APIRouter(prefix="/listings", tags=["listings"])


def _get_features(session: Session, listing_id: str) -> list[ExtractedFeature]:
    tags = session.exec(
        select(ListingFeature).where(ListingFeature.listing_id == listing_id)
    ).all()
    result = []
    for tag in tags:
        feature = session.get(Feature, tag.feature_id)
        if feature:
            result.append(ExtractedFeature(
                feature_id=feature.feature_id,
                name=feature.name,
                description=feature.description,
                score=tag.score,
            ))
    return result


def _extract_and_tag(session: Session, listing: Listing) -> list[ExtractedFeature]:
    extracted = llm_service.extract_listing_features(listing)
    result = []
    for f in extracted:
        # Upsert Feature by name so features are shared across listings (needed for correlation)
        feature = session.exec(select(Feature).where(Feature.name == f["name"])).first()
        if not feature:
            feature = Feature(name=f["name"], description=f.get("description"))
            session.add(feature)
            session.flush()  # populate feature_id before using it in the link

        tag = ListingFeature(
            listing_id=listing.listing_id,
            feature_id=feature.feature_id,
            score=f.get("score", 1.0),
        )
        session.add(tag)
        result.append(ExtractedFeature(
            feature_id=feature.feature_id,
            name=feature.name,
            description=feature.description,
            score=tag.score,
        ))
    session.commit()
    return result


@router.post("", response_model=ListingResponse, status_code=201)
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
        listing = existing

        # Return existing features without re-running LLM
        features = _get_features(session, listing.listing_id)
        if features:
            return ListingResponse(listing_id=listing.listing_id, features=features)
    else:
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

    # New listing (or existing with no features yet) — run LLM extraction
    features = _extract_and_tag(session, listing)
    return ListingResponse(listing_id=listing.listing_id, features=features)


@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    features = _get_features(session, listing_id)
    return ListingResponse(listing_id=listing.listing_id, features=features)


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
