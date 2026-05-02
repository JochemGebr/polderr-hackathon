from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature
from app.schemas import ExtractedFeature, ListingCreate, ListingResponse
from app.services import llm_service

router = APIRouter(prefix="/listings", tags=["listings"])


def _serialize(body: ListingCreate) -> dict:
    return body.model_dump()


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
        feature = session.exec(select(Feature).where(Feature.name == f["name"])).first()
        if not feature:
            feature = Feature(name=f["name"], description=f.get("description"))
            session.add(feature)
            session.flush()

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
    data = _serialize(body)
    existing = session.exec(
        select(Listing).where(Listing.external_id == body.external_id)
    ).first()

    if existing:
        for field, value in data.items():
            setattr(existing, field, value)
        session.add(existing)
        session.commit()
        listing = existing

        features = _get_features(session, listing.listing_id)
        if features:
            return ListingResponse(listing_id=listing.listing_id, features=features)
    else:
        listing = Listing(**data)
        session.add(listing)
        session.commit()
        session.refresh(listing)

    features = _extract_and_tag(session, listing)
    return ListingResponse(listing_id=listing.listing_id, features=features)