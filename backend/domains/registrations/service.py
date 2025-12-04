"""
Registration service for business logic
"""
from typing import List, Dict, Any
from common.exceptions import NotFoundError, CapacityError
from .repository import RegistrationRepository


class RegistrationService:
    """Service for registration business logic"""
    
    def __init__(self, registration_repo: RegistrationRepository, user_repo, event_repo):
        self.registration_repo = registration_repo
        self.user_repo = user_repo
        self.event_repo = event_repo
    
    def register_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Register a user for an event"""
        # Validate user exists
        if not self.user_repo.exists(user_id):
            raise NotFoundError(f"User {user_id} does not exist")
        
        # Get event
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} does not exist")
        
        # Check if already registered
        existing_registration = self.registration_repo.get_registration(user_id, event_id)
        if existing_registration:
            raise Exception(f"User {user_id} is already registered for event {event_id}")
        
        # Check capacity
        current_registrations = event.get('currentRegistrations', 0)
        capacity = event.get('capacity', 0)
        
        if current_registrations < capacity:
            # Create registration and increment capacity
            registration = self.registration_repo.create_registration(user_id, event_id)
            self.event_repo.update_capacity(event_id, 1)
            return {'type': 'registration', 'data': registration}
        else:
            # Event is full
            waitlist_enabled = event.get('waitlistEnabled', False)
            if waitlist_enabled:
                # Add to waitlist
                waitlist_entry = self.registration_repo.add_to_waitlist(user_id, event_id)
                return {'type': 'waitlist', 'data': waitlist_entry}
            else:
                raise CapacityError(f"Event {event_id} is at full capacity and waitlist is not enabled")
    
    def unregister_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Unregister a user from an event"""
        # Check if user is registered
        registration = self.registration_repo.get_registration(user_id, event_id)
        if not registration:
            raise NotFoundError(f"User {user_id} is not registered for event {event_id}")
        
        # Delete registration
        self.registration_repo.delete_registration(user_id, event_id)
        
        # Decrement capacity
        self.event_repo.update_capacity(event_id, -1)
        
        # Check for waitlist promotion
        first_waitlist = self.registration_repo.get_first_waitlist_entry(event_id)
        
        result = {
            'unregistered': True,
            'promoted': None
        }
        
        if first_waitlist:
            # Promote from waitlist
            promoted_user_id = first_waitlist['userId']
            timestamp = first_waitlist['addedAt']
            
            # Create registration for promoted user
            promoted_registration = self.registration_repo.create_registration(promoted_user_id, event_id)
            
            # Remove from waitlist
            self.registration_repo.remove_from_waitlist(event_id, promoted_user_id, timestamp)
            
            result['promoted'] = promoted_registration
        
        return result
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all events a user is registered for"""
        # Validate user exists
        if not self.user_repo.exists(user_id):
            raise NotFoundError(f"User {user_id} does not exist")
        
        # Get registrations
        registrations = self.registration_repo.get_user_registrations(user_id)
        
        # Fetch event details
        events = []
        for reg in registrations:
            event_id = reg['eventId']
            event = self.event_repo.get_by_id(event_id)
            if event:
                events.append(event)
        
        return events
    
    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for an event"""
        return self.registration_repo.get_event_registrations(event_id)
    
    def get_event_waitlist(self, event_id: str) -> List[Dict[str, Any]]:
        """Get waitlist for an event"""
        return self.registration_repo.get_event_waitlist(event_id)
