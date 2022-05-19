"""Schemas chatbot module."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel


class Action(str, Enum):
    CREATE_MEETING = "creazione_evento"
    GREETINGS = "welcome"


class CreateGoogleCredentials(BaseModel):
    name: str
    email: str
    timezone: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None

    class Config:
        orm_mode = True


class GoogleCredentialsSchema(BaseModel):
    id: int
    name: str
    email: str
    timezone: str
    access_token: str
    refresh_token: str
    created_at: datetime

    class Config:
        orm_mode = True
