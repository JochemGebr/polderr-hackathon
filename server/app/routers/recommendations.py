from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Listing, User
from app.services import aggregation_service, llm_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
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

    similar = aggregation_service.find_similar_applications(session, listing)
    principles = aggregation_service.get_principles()

    return llm_service.generate_recommendation(listing, user, similar, principles)
