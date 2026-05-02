import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def new_id() -> str:
    return str(uuid.uuid4())


class ListingFeature(SQLModel, table=True):
    listing_id: str = Field(foreign_key="listing.listing_id", primary_key=True)
    feature_id: str = Field(foreign_key="feature.feature_id", primary_key=True)


class PersonFeature(SQLModel, table=True):
    person_id: str = Field(foreign_key="person.person_id", primary_key=True)
    feature_id: str = Field(foreign_key="feature.feature_id", primary_key=True)


class MessageFeature(SQLModel, table=True):
    message_id: str = Field(foreign_key="message.message_id", primary_key=True)
    feature_id: str = Field(foreign_key="feature.feature_id", primary_key=True)


class Listing(SQLModel, table=True):
    listing_id: str = Field(default_factory=new_id, primary_key=True)
    external_id: str = Field(unique=True, index=True)
    url: str
    title: str
    description: str
    price: Optional[int] = None  # monthly rent in cents
    location: Optional[str] = None
    listing_type: Optional[str] = None  # room | apartment | studio | etc.

    applications: List["Application"] = Relationship(back_populates="listing")
    # features attached to this listing (many-to-many)
    features: List["Feature"] = Relationship(
        back_populates="listings", link_model=ListingFeature
    )
    # messages associated with this listing
    messages: List["Message"] = Relationship(back_populates="listing")


class User(SQLModel, table=True):
    user_id: str = Field(default_factory=new_id, primary_key=True)
    name: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[int] = None  # monthly net in euros
    age: Optional[int] = None
    has_pets: bool = False
    bio: Optional[str] = None  # free-text self description the LLM can use
    profile: Optional[str] = None  # JSON blob for extra structured data
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    applications: List["Application"] = Relationship(back_populates="user")


# status values: PENDING | INVITED | REJECTED | GHOSTED | ACCEPTED
class Application(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "listing_id"),)

    application_id: str = Field(default_factory=new_id, primary_key=True)
    user_id: str = Field(foreign_key="user.user_id", index=True)
    listing_id: str = Field(foreign_key="listing.listing_id", index=True)
    status: str = Field(default="PENDING")
    message: Optional[str] = None  # the message sent (or drafted) to the landlord
    result_notes: Optional[str] = None  # user-provided notes on why accepted/rejected
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="applications")
    listing: Optional[Listing] = Relationship(back_populates="applications")


class Feature(SQLModel, table=True):
    feature_id: str = Field(default_factory=new_id, primary_key=True)
    name: str
    description: str

    listings: List["Listing"] = Relationship(
        back_populates="features", link_model=ListingFeature
    )
    messages: List["Message"] = Relationship(
        back_populates="features", link_model=MessageFeature
    )
    persons: List["Person"] = Relationship(
        back_populates="features", link_model=PersonFeature
    )


class Person(SQLModel, table=True):
    person_id: str = Field(default_factory=new_id, primary_key=True)
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    text: Optional[str] = None

    messages: List["Message"] = Relationship(back_populates="person")
    features: List[Feature] = Relationship(
        back_populates="persons", link_model=PersonFeature
    )
    accepted_listings: List[Listing] = Relationship(back_populates="accepted_person")


class Message(SQLModel, table=True):
    message_id: str = Field(default_factory=new_id, primary_key=True)
    person_id: str = Field(foreign_key="person.person_id", index=True)
    listing_id: str = Field(foreign_key="listing.listing_id", index=True)
    message: str

    person: Optional[Person] = Relationship(back_populates="messages")
    listing: Optional[Listing] = Relationship(back_populates="messages")
    features: List[Feature] = Relationship(
        back_populates="messages", link_model=MessageFeature
    )
