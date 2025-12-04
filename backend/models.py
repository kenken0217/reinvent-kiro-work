from pydantic import BaseModel, Field
from typing import Optional

class EventCreate(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1)
    status: str = Field(..., pattern=r'^(active|inactive|cancelled|completed)$')

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    location: Optional[str] = Field(None, min_length=1)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1)
    status: Optional[str] = Field(None, pattern=r'^(active|inactive|cancelled|completed)$')

class Event(BaseModel):
    eventId: str
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str
