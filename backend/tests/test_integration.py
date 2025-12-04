"""
Integration tests for user registration system
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

client = TestClient(app)


class TestUserEndpoints:
    """Test user management endpoints"""
    
    @patch('domains.users.service.UserService.create_user')
    def test_create_user_success(self, mock_create):
        """Test successful user creation"""
        mock_create.return_value = {
            'userId': 'user123',
            'name': 'Test User',
            'createdAt': '2024-12-03T10:00:00Z'
        }
        
        response = client.post('/users', json={
            'userId': 'user123',
            'name': 'Test User'
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data['userId'] == 'user123'
        assert data['name'] == 'Test User'
    
    @patch('domains.users.service.UserService.create_user')
    def test_create_user_duplicate(self, mock_create):
        """Test creating duplicate user returns 409"""
        from common.exceptions import ConflictError
        mock_create.side_effect = ConflictError('User with ID user123 already exists')
        
        response = client.post('/users', json={
            'userId': 'user123',
            'name': 'Test User'
        })
        
        assert response.status_code == 409
    
    @patch('domains.users.service.UserService.get_user')
    def test_get_user_success(self, mock_get):
        """Test getting existing user"""
        mock_get.return_value = {
            'userId': 'user123',
            'name': 'Test User',
            'createdAt': '2024-12-03T10:00:00Z'
        }
        
        response = client.get('/users/user123')
        
        assert response.status_code == 200
        data = response.json()
        assert data['userId'] == 'user123'
    
    @patch('domains.users.service.UserService.get_user')
    def test_get_user_not_found(self, mock_get):
        """Test getting non-existent user returns 404"""
        mock_get.return_value = None
        
        response = client.get('/users/nonexistent')
        
        assert response.status_code == 404


class TestRegistrationEndpoints:
    """Test registration endpoints"""
    
    @patch('domains.registrations.service.RegistrationService.register_user')
    def test_register_user_success(self, mock_register):
        """Test successful registration"""
        mock_register.return_value = {
            'type': 'registration',
            'data': {
                'registrationId': 'reg123',
                'userId': 'user123',
                'eventId': 'event123',
                'registeredAt': '2024-12-03T10:00:00Z',
                'status': 'confirmed'
            }
        }
        
        response = client.post('/events/event123/registrations', json={
            'userId': 'user123'
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'registered'
        assert 'registration' in data
    
    @patch('domains.registrations.service.RegistrationService.register_user')
    def test_register_user_waitlist(self, mock_register):
        """Test registration when event is full (waitlist)"""
        mock_register.return_value = {
            'type': 'waitlist',
            'data': {
                'waitlistId': 'wait123',
                'userId': 'user123',
                'eventId': 'event123',
                'addedAt': '2024-12-03T10:00:00Z',
                'position': 1
            }
        }
        
        response = client.post('/events/event123/registrations', json={
            'userId': 'user123'
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data['status'] == 'waitlisted'
        assert 'waitlistEntry' in data
    
    @patch('domains.registrations.service.RegistrationService.register_user')
    def test_register_user_already_registered(self, mock_register):
        """Test registering when already registered returns 409"""
        from common.exceptions import ConflictError
        mock_register.side_effect = ConflictError('User user123 is already registered for event event123')
        
        response = client.post('/events/event123/registrations', json={
            'userId': 'user123'
        })
        
        assert response.status_code == 409
    
    @patch('domains.registrations.service.RegistrationService.register_user')
    def test_register_user_event_full(self, mock_register):
        """Test registering when event is full without waitlist returns 422"""
        from common.exceptions import CapacityError
        mock_register.side_effect = CapacityError('Event event123 is at full capacity and waitlist is not enabled')
        
        response = client.post('/events/event123/registrations', json={
            'userId': 'user123'
        })
        
        assert response.status_code == 422
    
    @patch('domains.registrations.service.RegistrationService.unregister_user')
    def test_unregister_user_success(self, mock_unregister):
        """Test successful unregistration"""
        mock_unregister.return_value = {
            'unregistered': True,
            'promoted': None
        }
        
        response = client.delete('/events/event123/registrations/user123')
        
        assert response.status_code == 200
        data = response.json()
        assert data['unregistered'] is True
    
    @patch('domains.registrations.service.RegistrationService.unregister_user')
    def test_unregister_with_promotion(self, mock_unregister):
        """Test unregistration with waitlist promotion"""
        mock_unregister.return_value = {
            'unregistered': True,
            'promoted': {
                'registrationId': 'reg456',
                'userId': 'user456',
                'eventId': 'event123',
                'registeredAt': '2024-12-03T10:00:00Z',
                'status': 'confirmed'
            }
        }
        
        response = client.delete('/events/event123/registrations/user123')
        
        assert response.status_code == 200
        data = response.json()
        assert data['unregistered'] is True
        assert 'promoted' in data
    
    @patch('domains.registrations.service.RegistrationService.unregister_user')
    def test_unregister_not_registered(self, mock_unregister):
        """Test unregistering when not registered returns 404"""
        from common.exceptions import NotFoundError
        mock_unregister.side_effect = NotFoundError('User user123 is not registered for event event123')
        
        response = client.delete('/events/event123/registrations/user123')
        
        assert response.status_code == 404
    
    @patch('domains.registrations.service.RegistrationService.get_event_registrations')
    def test_get_event_registrations(self, mock_get_regs):
        """Test getting event registrations"""
        mock_get_regs.return_value = [
            {
                'registrationId': 'reg123',
                'userId': 'user123',
                'eventId': 'event123',
                'registeredAt': '2024-12-03T10:00:00Z',
                'status': 'confirmed'
            }
        ]
        
        response = client.get('/events/event123/registrations')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['userId'] == 'user123'
    
    @patch('domains.registrations.service.RegistrationService.get_event_waitlist')
    def test_get_event_waitlist(self, mock_get_waitlist):
        """Test getting event waitlist"""
        mock_get_waitlist.return_value = [
            {
                'waitlistId': 'wait123',
                'userId': 'user456',
                'eventId': 'event123',
                'addedAt': '2024-12-03T10:00:00Z',
                'position': 1
            }
        ]
        
        response = client.get('/events/event123/waitlist')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['position'] == 1


class TestUserRegistrationsEndpoint:
    """Test user registrations listing endpoint"""
    
    @patch('domains.registrations.service.RegistrationService.get_user_registrations')
    def test_get_user_registrations(self, mock_get_regs):
        """Test getting user's registered events"""
        mock_get_regs.return_value = [
            {
                'PK': 'EVENT#event123',
                'SK': 'METADATA',
                'eventId': 'event123',
                'title': 'Test Event',
                'description': 'Test Description',
                'date': '2024-12-10',
                'location': 'Test Location',
                'capacity': 100,
                'organizer': 'Test Organizer',
                'status': 'active',
                'waitlistEnabled': False,
                'currentRegistrations': 50
            }
        ]
        
        response = client.get('/users/user123/registrations')
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['eventId'] == 'event123'
    
    @patch('domains.registrations.service.RegistrationService.get_user_registrations')
    def test_get_user_registrations_user_not_found(self, mock_get_regs):
        """Test getting registrations for non-existent user"""
        from common.exceptions import NotFoundError
        mock_get_regs.side_effect = NotFoundError('User nonexistent does not exist')
        
        response = client.get('/users/nonexistent/registrations')
        
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
