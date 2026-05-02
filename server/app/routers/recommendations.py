from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Listing, ListingFeature, User
from app.schemas import MotivationResponse
from app.services import llm_service
from app.services.aggregation_service import get_insights

router = APIRouter(prefix="/motivation", tags=["motivation"])


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


@router.get("/insights")
def get_insights_endpoint(
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
    return get_insights(session, listing, user)


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

    listing_features = _listing_features(session, listing_id)
    insights = get_insights(session, listing, user)

    motivation = llm_service.generate_motivation(
        listing, user, listing_features, session, insights
    )
    return MotivationResponse(motivation=motivation)
