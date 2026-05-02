from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", status_code=201)
def create_application(body: ApplicationCreate, session: Session = Depends(get_session)):
    existing = session.exec(
        select(Application).where(
            Application.user_id == body.user_id,
            Application.listing_id == body.listing_id,
        )
    ).first()

    if existing:
        if body.message:
            existing.message = body.message
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    application = Application(
        user_id=body.user_id,
        listing_id=body.listing_id,
        message=body.message,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


@router.patch("/{application_id}")
def update_application(
    application_id: str,
    body: ApplicationUpdate,
    session: Session = Depends(get_session),
):
    application = session.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    application.updated_at = datetime.utcnow()
    session.add(application)
    session.commit()
    session.refresh(application)
    return application

