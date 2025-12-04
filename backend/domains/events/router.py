"""
Event API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from common.database import DynamoDBClient
from common.dependencies import get_database
from common.exceptions import NotFoundError, ValidationError
from .models import Event, EventCreate, EventUpdate
from .repository import EventRepository
from .service import EventService


router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db: DynamoDBClient = Depends(get_database)) -> EventService:
    """Dependency for event service"""
    repository = EventRepository(db)
    return EventService(repository)


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    service: EventService = Depends(get_event_service)
):
    """Create a new event"""
    try:
        event_data = event.model_dump()
        created_event = service.create_event(event_data)
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Event])
def list_events(
    status_filter: Optional[str] = Query(None, description="Filter events by status"),
    service: EventService = Depends(get_event_service)
):
    """List all events"""
    try:
        events = service.list_events(status_filter)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=Event)
def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """Get event by ID"""
    try:
        event = service.get_event(event_id)
        return event
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: str,
    event_update: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    """Update an event"""
    try:
        update_data = event_update.model_dump(exclude_unset=True)
        updated_event = service.update_event(event_id, update_data)
        return updated_event
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """Delete an event"""
    try:
        service.delete_event(event_id)
        return {"message": "Event deleted successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
