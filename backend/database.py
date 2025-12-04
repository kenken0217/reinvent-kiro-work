import boto3
import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

# DynamoDB reserved keywords that need expression attribute names
RESERVED_KEYWORDS = {'status', 'capacity', 'date', 'location', 'description', 'name', 'position'}

class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'EventsTable')
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.table.put_item(Item=event_data)
            return event_data
        except ClientError as e:
            raise Exception(f"Error creating event: {e.response['Error']['Message']}")
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(Key={'eventId': event_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting event: {e.response['Error']['Message']}")
    
    def list_events(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            if status_filter:
                # Use FilterExpression with ExpressionAttributeNames for reserved keyword
                response = self.table.scan(
                    FilterExpression='#status_attr = :status_val',
                    ExpressionAttributeNames={'#status_attr': 'status'},
                    ExpressionAttributeValues={':status_val': status_filter}
                )
            else:
                response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error listing events: {e.response['Error']['Message']}")
    
    def update_event(self, event_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Build update expression with proper handling of reserved keywords
            update_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in update_data.items():
                # Use expression attribute names for reserved keywords
                if key.lower() in RESERVED_KEYWORDS:
                    attr_name = f"#{key}"
                    expression_attribute_names[attr_name] = key
                    update_parts.append(f"{attr_name} = :{key}")
                else:
                    update_parts.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value
            
            update_expression = "SET " + ", ".join(update_parts)
            
            update_params = {
                'Key': {'eventId': event_id},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if expression_attribute_names:
                update_params['ExpressionAttributeNames'] = expression_attribute_names
            
            response = self.table.update_item(**update_params)
            return response.get('Attributes')
        except ClientError as e:
            raise Exception(f"Error updating event: {e.response['Error']['Message']}")
    
    def delete_event(self, event_id: str) -> bool:
        try:
            self.table.delete_item(Key={'eventId': event_id})
            return True
        except ClientError as e:
            raise Exception(f"Error deleting event: {e.response['Error']['Message']}")
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user with single-table design pattern"""
        try:
            user_id = user_data['userId']
            item = {
                'PK': f"USER#{user_id}",
                'SK': 'METADATA',
                'userId': user_id,
                'name': user_data['name'],
                'createdAt': datetime.utcnow().isoformat() + 'Z'
            }
            
            # Use conditional write to prevent duplicate users
            self.table.put_item(
                Item=item,
                ConditionExpression='attribute_not_exists(PK)'
            )
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception(f"User with ID {user_id} already exists")
            raise Exception(f"Error creating user: {e.response['Error']['Message']}")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"USER#{user_id}",
                    'SK': 'METADATA'
                }
            )
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting user: {e.response['Error']['Message']}")
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        user = self.get_user(user_id)
        return user is not None
    
    # Registration operations
    def create_registration(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Create a registration for a user and event"""
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
            
            # Use conditional write to prevent duplicate registrations
            self.table.put_item(
                Item=registration_item,
                ConditionExpression='attribute_not_exists(PK) AND attribute_not_exists(SK)'
            )
            
            return registration_item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise Exception(f"User {user_id} is already registered for event {event_id}")
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
        """Get all registrations for an event using GSI1"""
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
    
    # Waitlist operations
    def add_to_waitlist(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Add user to event waitlist"""
        try:
            waitlist_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # Get current waitlist size to determine position
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
        """Get waitlist for an event (ordered by timestamp)"""
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
    
    # Update event to use single-table design
    def create_event_v2(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create event with single-table design pattern"""
        try:
            event_id = event_data.get('eventId', str(uuid.uuid4()))
            item = {
                'PK': f"EVENT#{event_id}",
                'SK': 'METADATA',
                'eventId': event_id,
                'title': event_data['title'],
                'description': event_data['description'],
                'date': event_data['date'],
                'location': event_data['location'],
                'capacity': event_data['capacity'],
                'organizer': event_data['organizer'],
                'status': event_data['status'],
                'waitlistEnabled': event_data.get('waitlistEnabled', False),
                'currentRegistrations': event_data.get('currentRegistrations', 0),
                'version': 1
            }
            
            self.table.put_item(Item=item)
            return item
        except ClientError as e:
            raise Exception(f"Error creating event: {e.response['Error']['Message']}")
    
    def get_event_v2(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event with single-table design pattern"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': 'METADATA'
                }
            )
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting event: {e.response['Error']['Message']}")
    
    def update_event_capacity(self, event_id: str, increment: int) -> Dict[str, Any]:
        """Update event capacity atomically"""
        try:
            response = self.table.update_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': 'METADATA'
                },
                UpdateExpression='SET currentRegistrations = currentRegistrations + :inc, version = version + :one',
                ExpressionAttributeValues={
                    ':inc': increment,
                    ':one': 1
                },
                ReturnValues='ALL_NEW'
            )
            return response.get('Attributes')
        except ClientError as e:
            raise Exception(f"Error updating event capacity: {e.response['Error']['Message']}")


# Create database client instance
db_client = DynamoDBClient()

