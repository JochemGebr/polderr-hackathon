import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import User
from app.schemas import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=201)
def create_user(body: UserCreate, session: Session = Depends(get_session)):
    user = User(
        name=body.name,
        occupation=body.occupation,
        income=body.income,
        age=body.age,
        has_pets=body.has_pets,
        bio=body.bio
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}")
def get_user(user_id: str, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}")
def update_user(user_id: str, body: UserUpdate, session: Session = Depends(get_session)):
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
    return user
