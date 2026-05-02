from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import Feature
from app.schemas import FeatureCreate, FeatureRead

router = APIRouter(prefix="/features", tags=["features"])


@router.post("", response_model=FeatureRead, status_code=201)
def create_feature(body: FeatureCreate, session: Session = Depends(get_session)):
    feature = Feature(name=body.name, description=body.description)
    session.add(feature)
    session.commit()
    session.refresh(feature)
    return feature


@router.get("", response_model=list[FeatureRead])
def list_features(session: Session = Depends(get_session)):
    return session.exec(select(Feature)).all()


@router.get("/{feature_id}", response_model=FeatureRead)
def get_feature(feature_id: str, session: Session = Depends(get_session)):
    feature = session.get(Feature, feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature
