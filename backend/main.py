from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import List, Optional
from models import (
    Event, EventCreate, EventUpdate,
    User, UserCreate,
    Registration, RegistrationCreate,
    WaitlistEntry
)
from database import db_client
from services import user_service, registration_service

app = FastAPI(title="Event Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Event Management API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    try:
        event_data = event.model_dump()
        
        # If eventId is provided in the request, use it; otherwise generate one
        if 'eventId' not in event_data or not event_data.get('eventId'):
            import uuid
            event_data['eventId'] = str(uuid.uuid4())
        
        # Use the new single-table design method
        created_event = db_client.create_event_v2(event_data)
        return created_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events", response_model=List[Event])
def list_events(status: Optional[str] = Query(None, description="Filter events by status")):
    try:
        events = db_client.list_events(status_filter=status)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    try:
        event = db_client.get_event_v2(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    try:
        # Check if event exists
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Only update fields that are provided
        update_data = event_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_event = db_client.update_event(event_id, update_data)
        return updated_event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(event_id: str):
    try:
        # Check if event exists
        existing_event = db_client.get_event(event_id)
        if not existing_event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        db_client.delete_event(event_id)
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User endpoints
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_data = user.model_dump()
        created_user = user_service.create_user(user_data)
        return created_user
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/registrations", response_model=List[Event])
def get_user_registrations(user_id: str):
    """Get all events a user is registered for"""
    try:
        events = registration_service.get_user_registrations(user_id)
        return events
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Registration endpoints
@app.post("/events/{event_id}/registrations", status_code=status.HTTP_201_CREATED)
def create_registration(event_id: str, user_data: dict):
    """Register a user for an event"""
    try:
        user_id = user_data.get('userId')
        if not user_id:
            raise HTTPException(status_code=400, detail="userId is required")
        
        result = registration_service.register_user(user_id, event_id)
        
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
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "already registered" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        elif "full capacity" in error_msg:
            raise HTTPException(status_code=422, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_200_OK)
def delete_registration(event_id: str, user_id: str):
    """Unregister a user from an event"""
    try:
        result = registration_service.unregister_user(user_id, event_id)
        
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
    except Exception as e:
        error_msg = str(e)
        if "not registered" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/events/{event_id}/registrations", response_model=List[Registration])
def get_event_registrations(event_id: str):
    """Get all registrations for an event"""
    try:
        registrations = registration_service.get_event_registrations(event_id)
        return registrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}/waitlist", response_model=List[WaitlistEntry])
def get_event_waitlist(event_id: str):
    """Get waitlist for an event"""
    try:
        waitlist = registration_service.get_event_waitlist(event_id)
        return waitlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda handler
handler = Mangum(app)
