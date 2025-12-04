"""
Event service for business logic
"""
from typing import Optional, List, Dict, Any
from common.exceptions import NotFoundError, ValidationError
from .repository import EventRepository


class EventService:
    """Service for event business logic"""
    
    def __init__(self, repository: EventRepository):
        self.repository = repository
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
        return self.repository.create(event_data)
    
    def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get event by ID"""
        event = self.repository.get_by_id(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")
        return event
    
    def list_events(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events"""
        return self.repository.list_all(status_filter)
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an event"""
        # Check if event exists
        existing_event = self.repository.get_by_id(event_id)
        if not existing_event:
            raise NotFoundError(f"Event {event_id} not found")
        
        if not update_data:
            raise ValidationError("No fields to update")
        
        return self.repository.update(event_id, update_data)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        # Check if event exists
        existing_event = self.repository.get_by_id(event_id)
        if not existing_event:
            raise NotFoundError(f"Event {event_id} not found")
        
        return self.repository.delete(event_id)
