from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, col, select

from app.db import engine, get_session
from app.models import Application, Feature, Listing, ListingFeature, User, UserFeature
from app.schemas import UserCreate, UserUpdate
from app.services import llm_service

router = APIRouter(prefix="/users", tags=["users"])


def _extract_features_bg(user_id: str) -> None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user:
            llm_service.extract_and_store_user_features(user, session)


@router.post("", status_code=201)
def create_user(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = User(
        name=body.name,
        gender=body.gender,
        occupation=body.occupation,
        income=body.income,
        age=body.age,
        has_pets=body.has_pets,
        bio=body.bio
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    background_tasks.add_task(_extract_features_bg, user.user_id)
    return user


@router.get("/{user_id}")
def get_user(user_id: str, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    background_tasks.add_task(_extract_features_bg, user.user_id)
    return user


@router.get("/{user_id}/features")
def get_user_features(
    user_id: str, session: Session = Depends(get_session)
):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    rows = session.exec(
        select(UserFeature).where(UserFeature.user_id == user_id)
    ).all()
    result = []
    for uf in rows:
        feature = session.get(Feature, uf.feature_id)
        if feature:
            result.append({"name": feature.name, "score": uf.score})
    return result


@router.get("/{user_id}/applications")
def get_user_applications(
    user_id: str, session: Session = Depends(get_session)
):
    import traceback
    try:
     return _get_user_applications(user_id, session)
    except Exception:
     raise HTTPException(status_code=500, detail=traceback.format_exc())

def _get_user_applications(user_id: str, session):
    if not session.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    user_features = session.exec(
        select(UserFeature).where(UserFeature.user_id == user_id)
    ).all()
    user_score_map = {uf.feature_id: uf.score for uf in user_features}

    applications = session.exec(
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(col(Application.applied_at).desc())
    ).all()

    result = []
    for app in applications:
        listing = session.get(Listing, app.listing_id)
        if not listing:
            continue

        listing_features = session.exec(
            select(ListingFeature).where(
                ListingFeature.listing_id == listing.listing_id
            )
        ).all()

        compatibility = None
        if listing_features and user_score_map:
            total = sum(lf.score for lf in listing_features)
            matched = sum(
                lf.score * user_score_map.get(lf.feature_id, 0.0)
                for lf in listing_features
            )
            if total > 0:
                compatibility = round(matched / total, 2)

        result.append({
            "application_id": app.application_id,
            "status": app.status,
            "applied_at": app.applied_at.isoformat(),
            "listing": {
                "listing_id": listing.listing_id,
                "title": listing.title,
                "location": listing.location,
                "price": listing.price,
            },
            "compatibility": compatibility,
        })
    return result
