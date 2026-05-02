from typing import Any, Literal, Optional  # Any kept for UserCreate.profile

from pydantic import BaseModel

ApplicationStatus = Literal["PENDING", "INVITED", "REJECTED", "GHOSTED", "ACCEPTED"]


class ListingCreate(BaseModel):
    user_id: str
    external_id: str
    url: str
    title: str
    description: str
    price: Optional[float] = None
    location: Optional[str] = None
    details: Optional[str] = None
    ideal_tenant: Optional[str] = None
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


class FeatureScore(BaseModel):
    name: str
    pretty_name: str        # display-ready: "Quiet Person" not "quiet_person"
    score: float            # -1.0 (missing/weak) to +1.0 (strong match)


class MatchResponse(BaseModel):
    listing_id: str
    match_score: float          # 0.0–1.0 overall compatibility
    features: list[FeatureScore]


class RecommendationResponse(BaseModel):
    message: str


# Kept for internal use by feature tag endpoints
class ExtractedFeature(BaseModel):
    feature_id: str
    name: str
    description: Optional[str] = None
    score: float


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
