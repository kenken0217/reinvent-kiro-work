"""
Business logic services for user registration system
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from database import db_client


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user
        
        Args:
            user_data: Dictionary containing userId and name
            
        Returns:
            Created user data
            
        Raises:
            Exception: If user already exists or creation fails
        """
        return self.db.create_user(user_data)
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            User data if found, None otherwise
        """
        return self.db.get_user(user_id)
    
    def user_exists(self, user_id: str) -> bool:
        """
        Check if user exists
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user exists, False otherwise
        """
        return self.db.user_exists(user_id)


class RegistrationService:
    """Service for registration and waitlist management"""
    
    def __init__(self, db_client):
        self.db = db_client
    
    def register_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """
        Register a user for an event
        
        Handles capacity checking and waitlist logic:
        - If event has capacity, creates registration and decrements capacity
        - If event is full and has waitlist, adds user to waitlist
        - If event is full without waitlist, raises exception
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            Registration or WaitlistEntry data
            
        Raises:
            Exception: If user/event doesn't exist, user already registered, or event full
        """
        # Validate user exists
        if not self.db.user_exists(user_id):
            raise Exception(f"User {user_id} does not exist")
        
        # Get event
        event = self.db.get_event_v2(event_id)
        if not event:
            raise Exception(f"Event {event_id} does not exist")
        
        # Check if already registered
        existing_registration = self.db.get_registration(user_id, event_id)
        if existing_registration:
            raise Exception(f"User {user_id} is already registered for event {event_id}")
        
        # Check capacity
        current_registrations = event.get('currentRegistrations', 0)
        capacity = event.get('capacity', 0)
        
        if current_registrations < capacity:
            # Create registration and increment capacity
            registration = self.db.create_registration(user_id, event_id)
            self.db.update_event_capacity(event_id, 1)
            return {'type': 'registration', 'data': registration}
        else:
            # Event is full
            waitlist_enabled = event.get('waitlistEnabled', False)
            if waitlist_enabled:
                # Add to waitlist
                waitlist_entry = self.db.add_to_waitlist(user_id, event_id)
                return {'type': 'waitlist', 'data': waitlist_entry}
            else:
                raise Exception(f"Event {event_id} is at full capacity and waitlist is not enabled")
    
    def unregister_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """
        Unregister a user from an event
        
        Handles waitlist promotion:
        - Removes registration and decrements capacity
        - If waitlist has entries, promotes first user automatically
        
        Args:
            user_id: User identifier
            event_id: Event identifier
            
        Returns:
            Result dictionary with unregistration status and promotion info
            
        Raises:
            Exception: If user is not registered for the event
        """
        # Check if user is registered
        registration = self.db.get_registration(user_id, event_id)
        if not registration:
            raise Exception(f"User {user_id} is not registered for event {event_id}")
        
        # Delete registration
        self.db.delete_registration(user_id, event_id)
        
        # Decrement capacity
        self.db.update_event_capacity(event_id, -1)
        
        # Check for waitlist promotion
        first_waitlist = self.db.get_first_waitlist_entry(event_id)
        
        result = {
            'unregistered': True,
            'promoted': None
        }
        
        if first_waitlist:
            # Promote from waitlist
            promoted_user_id = first_waitlist['userId']
            timestamp = first_waitlist['addedAt']
            
            # Create registration for promoted user
            promoted_registration = self.db.create_registration(promoted_user_id, event_id)
            
            # Remove from waitlist
            self.db.remove_from_waitlist(event_id, promoted_user_id, timestamp)
            
            # Capacity stays the same (one out, one in)
            
            result['promoted'] = promoted_registration
        
        return result
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all events a user is registered for
        
        Args:
            user_id: User identifier
            
        Returns:
            List of event data for registered events
        """
        # Validate user exists
        if not self.db.user_exists(user_id):
            raise Exception(f"User {user_id} does not exist")
        
        # Get registrations
        registrations = self.db.get_user_registrations(user_id)
        
        # Fetch event details for each registration
        events = []
        for reg in registrations:
            event_id = reg['eventId']
            event = self.db.get_event_v2(event_id)
            if event:
                events.append(event)
        
        return events
    
    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get all registrations for an event
        
        Args:
            event_id: Event identifier
            
        Returns:
            List of registration data
        """
        return self.db.get_event_registrations(event_id)
    
    def get_event_waitlist(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get waitlist for an event
        
        Args:
            event_id: Event identifier
            
        Returns:
            List of waitlist entries ordered by addition time
        """
        return self.db.get_event_waitlist(event_id)


# Create service instances
user_service = UserService(db_client)
registration_service = RegistrationService(db_client)
