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


@router.get("/listing/{listing_id}", response_model=list[MessageRead])
def get_messages_for_listing(listing_id: str, session: Session = Depends(get_session)):
    return session.exec(
        select(Message).where(Message.listing_id == listing_id)
    ).all()


@router.get("/{message_id}", response_model=MessageRead)
def get_message(message_id: str, session: Session = Depends(get_session)):
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post("/{message_id}/features/{feature_id}", status_code=201)
def tag_feature(message_id: str, feature_id: str, session: Session = Depends(get_session)):
    if not session.get(Message, message_id):
        raise HTTPException(status_code=404, detail="Message not found")
    if not session.get(Feature, feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")

    existing = session.get(MessageFeature, (message_id, feature_id))
    if existing:
        return existing

    tag = MessageFeature(message_id=message_id, feature_id=feature_id)
    session.add(tag)
    session.commit()
    return tag


@router.delete("/{message_id}/features/{feature_id}", status_code=204)
def untag_feature(message_id: str, feature_id: str, session: Session = Depends(get_session)):
    tag = session.get(MessageFeature, (message_id, feature_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
