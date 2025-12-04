"""
Registration domain models
"""
from pydantic import BaseModel, Field


class RegistrationCreate(BaseModel):
    userId: str = Field(..., min_length=1)
    eventId: str = Field(..., min_length=1)


class Registration(BaseModel):
    registrationId: str
    userId: str
    eventId: str
    registeredAt: str  # ISO 8601 timestamp
    status: str = "confirmed"


class WaitlistEntry(BaseModel):
    waitlistId: str
    userId: str
    eventId: str
    addedAt: str  # ISO 8601 timestamp
    position: int
