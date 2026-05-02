import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature, Match, User
from app.schemas import ExtractedFeature, FeatureScore, ListingCreate, MatchResponse
from app.services import llm_service
from app.services.aggregation_service import compute_match, get_insights

router = APIRouter(prefix="/listings", tags=["listings"])


def _serialize(body: ListingCreate) -> dict:
    data = body.model_dump(exclude={"user_id"})
    if data.get("accepted_occupations") is not None:
        data["accepted_occupations"] = json.dumps(data["accepted_occupations"])
    return data


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
    extracted = llm_service.extract_listing_features(listing, session)
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


def _upsert_match(
    session: Session,
    user_id: str,
    listing_id: str,
    score: float,
    features: list[dict],
) -> None:
    existing = session.exec(
        select(Match).where(Match.user_id == user_id, Match.listing_id == listing_id)
    ).first()
    if existing:
        existing.match_score = score
        existing.features = json.dumps(features)
        session.add(existing)
    else:
        session.add(Match(
            user_id=user_id,
            listing_id=listing_id,
            match_score=score,
            features=json.dumps(features),
        ))
    session.commit()


@router.post("", response_model=MatchResponse, status_code=201)
def upsert_listing(body: ListingCreate, session: Session = Depends(get_session)):
    user = session.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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
    else:
        listing = Listing(**data)
        session.add(listing)
        session.commit()
        session.refresh(listing)

    # Extract features (skip if already cached)
    if not _get_features(session, listing.listing_id):
        _extract_and_tag(session, listing)

    # Compute match for this user
    insights = get_insights(session, listing, user)
    score, features = compute_match(insights)
    _upsert_match(session, body.user_id, listing.listing_id, score, features)

    return MatchResponse(
        listing_id=listing.listing_id,
        match_score=score,
        features=[FeatureScore(**f) for f in features],
    )


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
