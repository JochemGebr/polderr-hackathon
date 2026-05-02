from typing import Any, Literal, Optional

from pydantic import BaseModel

ApplicationStatus = Literal["PENDING", "INVITED", "REJECTED", "GHOSTED", "ACCEPTED"]


class ListingCreate(BaseModel):
    external_id: str
    url: str
    title: str
    description: str
    price: Optional[int] = None  # monthly rent in cents
    location: Optional[str] = None
    listing_type: Optional[str] = None
    raw: dict[str, Any]  # full scraped payload — store verbatim
    accepted_person_id: Optional[str] = None


class UserCreate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[int] = None
    age: Optional[int] = None
    has_pets: bool = False
    bio: Optional[str] = None
    profile: Optional[dict[str, Any]] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[int] = None
    age: Optional[int] = None
    has_pets: Optional[bool] = None
    bio: Optional[str] = None
    profile: Optional[dict[str, Any]] = None


class ApplicationCreate(BaseModel):
    user_id: str
    listing_id: str
    message: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    message: Optional[str] = None
    result_notes: Optional[str] = None


class ExtractedFeature(BaseModel):
    feature_id: str
    name: str
    description: Optional[str] = None
    score: float


class ListingResponse(BaseModel):
    listing_id: str
    features: list[ExtractedFeature]


class MotivationResponse(BaseModel):
    motivation: str


class FeatureCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FeatureRead(FeatureCreate):
    feature_id: str


class PersonCreate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    text: Optional[str] = None


class PersonRead(PersonCreate):
    person_id: str


class MessageCreate(BaseModel):
    person_id: str
    listing_id: str
    message: str


class MessageRead(MessageCreate):
    message_id: str
