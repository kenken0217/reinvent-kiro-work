from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import List, Optional
from models import Event, EventCreate, EventUpdate
from database import db_client

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
        
        created_event = db_client.create_event(event_data)
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
        event = db_client.get_event(event_id)
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

# Lambda handler
handler = Mangum(app)
