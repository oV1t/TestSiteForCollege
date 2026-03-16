from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    group_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.STUDENT)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    choice_sets: List["ChoiceSet"] = Relationship(back_populates="user")

class Discipline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    title: str
    short_info: Optional[str] = None
    doc_url: Optional[str] = None
    active: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    choices: List["Choice"] = Relationship(back_populates="discipline")

class Campaign(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_date: datetime
    end_date: datetime
    min_choices: int = Field(default=2)
    max_choices: int = Field(default=3)
    active: bool = Field(default=True)

    choice_sets: List["ChoiceSet"] = Relationship(back_populates="campaign")

class ChoiceSet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    campaign_id: int = Field(foreign_key="campaign.id")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="choice_sets")
    campaign: Campaign = Relationship(back_populates="choice_sets")
    choices: List["Choice"] = Relationship(back_populates="choice_set")

class Choice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    choice_set_id: int = Field(foreign_key="choiceset.id")
    discipline_id: int = Field(foreign_key="discipline.id")
    priority: int = Field(ge=1, le=3)

    choice_set: ChoiceSet = Relationship(back_populates="choices")
    discipline: Discipline = Relationship(back_populates="choices")

class SyncState(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    last_synced_date: date
    last_sync_status: str
    last_error: Optional[str] = None
