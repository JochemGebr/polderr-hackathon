from datetime import datetime
from typing import List, Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
import uuid


def new_id() -> str:
    return str(uuid.uuid4())


class Listing(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    external_id: str = Field(unique=True, index=True)
    url: str
    title: str
    description: str
    price: Optional[int] = None         # monthly rent in cents
    location: Optional[str] = None
    listing_type: Optional[str] = None  # room | apartment | studio | etc.
    raw: str                             # raw JSON blob from the scraper
    extracted_features: Optional[str] = None  # JSON blob, written by llm_service
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    applications: List["Application"] = Relationship(back_populates="listing")


class User(SQLModel, table=True):
    id: str = Field(default_factory=new_id, primary_key=True)
    name: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[int] = None   # monthly net in euros
    age: Optional[int] = None
    has_pets: bool = False
    bio: Optional[str] = None      # free-text self description the LLM can use
    profile: Optional[str] = None  # JSON blob for extra structured data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    applications: List["Application"] = Relationship(back_populates="user")


# status values: PENDING | INVITED | REJECTED | GHOSTED | ACCEPTED
class Application(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "listing_id"),)

    id: str = Field(default_factory=new_id, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    listing_id: str = Field(foreign_key="listing.id", index=True)
    status: str = Field(default="PENDING")
    message: Optional[str] = None      # the message sent (or drafted) to the landlord
    result_notes: Optional[str] = None # user-provided notes on why accepted/rejected
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="applications")
    listing: Optional[Listing] = Relationship(back_populates="applications")
