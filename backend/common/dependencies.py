"""
FastAPI dependency injection functions
"""
from typing import Generator
from .database import DynamoDBClient, get_db_client


def get_database() -> Generator[DynamoDBClient, None, None]:
    """Dependency for getting database client"""
    db = get_db_client()
    try:
        yield db
    finally:
        pass  # Cleanup if needed
