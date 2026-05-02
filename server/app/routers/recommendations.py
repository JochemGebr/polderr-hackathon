import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature, Match, User
from app.schemas import RecommendationResponse
from app.services import llm_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


def _listing_features(session: Session, listing_id: str) -> list[dict]:
    tags = session.exec(
        select(ListingFeature).where(ListingFeature.listing_id == listing_id)
    ).all()
    result = []
    for tag in tags:
        feature = session.get(Feature, tag.feature_id)
        if feature:
            result.append({
                "name": feature.name,
                "description": feature.description,
                "score": tag.score,
            })
    return result


@router.post("", response_model=RecommendationResponse)
def get_recommendation(
    listing_id: str,
    user_id: str,
    session: Session = Depends(get_session),
):
    listing = session.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    match = session.exec(
        select(Match).where(Match.user_id == user_id, Match.listing_id == listing_id)
    ).first()
    if not match:
        raise HTTPException(
            status_code=404,
            detail="No match found — POST the listing first to generate match data",
        )

    all_features = json.loads(match.features)
    strengths = [f for f in all_features if f["score"] > 0]
    weaknesses = [f for f in all_features if f["score"] < 0]
    listing_features = _listing_features(session, listing_id)

    message = llm_service.generate_motivation(
        listing, user, listing_features, session, strengths, weaknesses
    )
    return RecommendationResponse(message=message)
