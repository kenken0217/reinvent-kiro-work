"""
Registration repository for data access
"""
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError
from common.database import DynamoDBClient
from common.exceptions import ConflictError


class RegistrationRepository:
    """Repository for registration data access"""
    
    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client
        self.table = db_client.get_table()
    
    def create_registration(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Create a registration"""
        try:
            registration_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            registration_item = {
                'PK': f"USER#{user_id}",
                'SK': f"REG#{event_id}",
                'GSI1PK': f"EVENT#{event_id}",
                'GSI1SK': f"REG#{user_id}",
                'registrationId': registration_id,
                'userId': user_id,
                'eventId': event_id,
                'registeredAt': timestamp,
                'status': 'confirmed'
            }
            
            self.table.put_item(
                Item=registration_item,
                ConditionExpression='attribute_not_exists(PK) AND attribute_not_exists(SK)'
            )
            
            return registration_item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ConflictError(f"User {user_id} is already registered for event {event_id}")
            raise Exception(f"Error creating registration: {e.response['Error']['Message']}")
    
    def get_registration(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific registration"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': f"REG#{event_id}"
                }
            )
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting registration: {e.response['Error']['Message']}")
    
    def delete_registration(self, user_id: str, event_id: str) -> bool:
        """Delete a registration"""
        try:
            self.table.delete_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': f"REG#{event_id}"
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Error deleting registration: {e.response['Error']['Message']}")
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for a user"""
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f"USER#{user_id}",
                    ':sk_prefix': 'REG#'
                }
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error getting user registrations: {e.response['Error']['Message']}")
    
    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """Get all registrations for an event"""
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='GSI1PK = :gsi1pk AND begins_with(GSI1SK, :gsi1sk_prefix)',
                ExpressionAttributeValues={
                    ':gsi1pk': f"EVENT#{event_id}",
                    ':gsi1sk_prefix': 'REG#'
                }
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error getting event registrations: {e.response['Error']['Message']}")
    
    def add_to_waitlist(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Add user to event waitlist"""
        try:
            waitlist_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Get current waitlist size
            waitlist = self.get_event_waitlist(event_id)
            position = len(waitlist) + 1
            
            waitlist_item = {
                'PK': f"EVENT#{event_id}",
                'SK': f"WAIT#{timestamp}#{user_id}",
                'waitlistId': waitlist_id,
                'userId': user_id,
                'eventId': event_id,
                'addedAt': timestamp,
                'position': position
            }
            
            self.table.put_item(Item=waitlist_item)
            return waitlist_item
        except ClientError as e:
            raise Exception(f"Error adding to waitlist: {e.response['Error']['Message']}")
    
    def get_event_waitlist(self, event_id: str) -> List[Dict[str, Any]]:
        """Get waitlist for an event"""
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f"EVENT#{event_id}",
                    ':sk_prefix': 'WAIT#'
                }
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error getting waitlist: {e.response['Error']['Message']}")
    
    def remove_from_waitlist(self, event_id: str, user_id: str, timestamp: str) -> bool:
        """Remove user from waitlist"""
        try:
            self.table.delete_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': f"WAIT#{timestamp}#{user_id}"
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Error removing from waitlist: {e.response['Error']['Message']}")
    
    def get_first_waitlist_entry(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get the first person on the waitlist"""
        try:
            response = self.table.query(
                KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
                ExpressionAttributeValues={
                    ':pk': f"EVENT#{event_id}",
                    ':sk_prefix': 'WAIT#'
                },
                Limit=1
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            raise Exception(f"Error getting first waitlist entry: {e.response['Error']['Message']}")
