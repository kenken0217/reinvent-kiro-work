"""
Registration API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from common.database import DynamoDBClient
from common.dependencies import get_database
from common.exceptions import NotFoundError, ConflictError, CapacityError
from domains.events.models import Event
from domains.events.repository import EventRepository
from domains.users.repository import UserRepository
from .models import Registration, WaitlistEntry
from .repository import RegistrationRepository
from .service import RegistrationService


router = APIRouter(tags=["registrations"])


def get_registration_service(db: DynamoDBClient = Depends(get_database)) -> RegistrationService:
    """Dependency for registration service"""
    registration_repo = RegistrationRepository(db)
    user_repo = UserRepository(db)
    event_repo = EventRepository(db)
    return RegistrationService(registration_repo, user_repo, event_repo)


@router.post("/events/{event_id}/registrations", status_code=status.HTTP_201_CREATED)
def create_registration(
    event_id: str,
    user_data: dict,
    service: RegistrationService = Depends(get_registration_service)
):
    """Register a user for an event"""
    try:
        user_id = user_data.get('userId')
        if not user_id:
            raise HTTPException(status_code=400, detail="userId is required")
        
        result = service.register_user(user_id, event_id)
        
        if result['type'] == 'registration':
            return {
                "status": "registered",
                "registration": result['data']
            }
        else:  # waitlist
            return {
                "status": "waitlisted",
                "waitlistEntry": result['data']
            }
    except HTTPException:
        raise
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except CapacityError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_200_OK)
def delete_registration(
    event_id: str,
    user_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Unregister a user from an event"""
    try:
        result = service.unregister_user(user_id, event_id)
        
        response = {
            "message": "Successfully unregistered",
            "unregistered": result['unregistered']
        }
        
        if result['promoted']:
            response['promoted'] = {
                "message": "User promoted from waitlist",
                "registration": result['promoted']
            }
        
        return response
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/registrations", response_model=List[Registration])
def get_event_registrations(
    event_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Get all registrations for an event"""
    try:
        registrations = service.get_event_registrations(event_id)
        return registrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/waitlist", response_model=List[WaitlistEntry])
def get_event_waitlist(
    event_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Get waitlist for an event"""
    try:
        waitlist = service.get_event_waitlist(event_id)
        return waitlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/registrations", response_model=List[Event])
def get_user_registrations(
    user_id: str,
    service: RegistrationService = Depends(get_registration_service)
):
    """Get all events a user is registered for"""
    try:
        events = service.get_user_registrations(user_id)
        return events
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
