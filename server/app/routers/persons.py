from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Feature, Person, PersonFeature
from app.schemas import PersonCreate, PersonRead

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonRead, status_code=201)
def create_person(body: PersonCreate, session: Session = Depends(get_session)):
    person = Person(**body.model_dump())
    session.add(person)
    session.commit()
    session.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: str, session: Session = Depends(get_session)):
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonRead)
def update_person(person_id: str, body: PersonCreate, session: Session = Depends(get_session)):
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(person, field, value)

    session.add(person)
    session.commit()
    session.refresh(person)
    return person


@router.post("/{person_id}/features/{feature_id}", status_code=201)
def tag_feature(person_id: str, feature_id: str, session: Session = Depends(get_session)):
    if not session.get(Person, person_id):
        raise HTTPException(status_code=404, detail="Person not found")
    if not session.get(Feature, feature_id):
        raise HTTPException(status_code=404, detail="Feature not found")

    existing = session.get(PersonFeature, (person_id, feature_id))
    if existing:
        return existing

    tag = PersonFeature(person_id=person_id, feature_id=feature_id)
    session.add(tag)
    session.commit()
    return tag


@router.delete("/{person_id}/features/{feature_id}", status_code=204)
def untag_feature(person_id: str, feature_id: str, session: Session = Depends(get_session)):
    tag = session.get(PersonFeature, (person_id, feature_id))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
