"""
User domain models
"""
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)


class User(BaseModel):
    userId: str
    name: str
    createdAt: str  # ISO 8601 timestamp
