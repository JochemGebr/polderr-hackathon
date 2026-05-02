from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Listing, ListingFeature, Feature, User
from app.schemas import MotivationResponse
from app.services import llm_service

router = APIRouter(prefix="/motivation", tags=["motivation"])


@router.get("", response_model=MotivationResponse)
def get_motivation(
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

    # Fetch listing features with scores
    tags = session.exec(
        select(ListingFeature).where(ListingFeature.listing_id == listing_id)
    ).all()
    listing_features = []
    for tag in tags:
        feature = session.get(Feature, tag.feature_id)
        if feature:
            listing_features.append({
                "name": feature.name,
                "description": feature.description,
                "score": tag.score,
            })

    motivation = llm_service.generate_motivation(
        listing, user, listing_features, session
    )
    return MotivationResponse(motivation=motivation)
