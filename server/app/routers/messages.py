from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature, Message, MessageFeature
from app.schemas import MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageRead, status_code=201)
def create_message(body: MessageCreate, session: Session = Depends(get_session)):
    message = Message(**body.model_dump())
    session.add(message)
    session.commit()
    session.refresh(message)
    return message