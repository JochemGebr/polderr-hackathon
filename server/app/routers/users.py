import json
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session

from app.db import engine, get_session
from app.models import User
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

    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)
    background_tasks.add_task(_extract_features_bg, user.user_id)
    return user
