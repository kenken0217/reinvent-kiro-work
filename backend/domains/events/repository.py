"""
Event repository for data access
"""
import uuid
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
from common.database import DynamoDBClient
from common.exceptions import NotFoundError, ConflictError


# DynamoDB reserved keywords
RESERVED_KEYWORDS = {'status', 'capacity', 'date', 'location', 'description'}


class EventRepository:
    """Repository for event data access"""
    
    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client
        self.table = db_client.get_table()
    
    def create(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event"""
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
    
    def get_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID"""
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
    
    def list_all(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all events with optional status filter"""
        try:
            if status_filter:
                response = self.table.scan(
                    FilterExpression='#status_attr = :status_val AND begins_with(PK, :pk_prefix)',
                    ExpressionAttributeNames={'#status_attr': 'status'},
                    ExpressionAttributeValues={
                        ':status_val': status_filter,
                        ':pk_prefix': 'EVENT#'
                    }
                )
            else:
                response = self.table.scan(
                    FilterExpression='begins_with(PK, :pk_prefix)',
                    ExpressionAttributeValues={':pk_prefix': 'EVENT#'}
                )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error listing events: {e.response['Error']['Message']}")
    
    def update(self, event_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an event"""
        try:
            update_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in update_data.items():
                if key.lower() in RESERVED_KEYWORDS:
                    attr_name = f"#{key}"
                    expression_attribute_names[attr_name] = key
                    update_parts.append(f"{attr_name} = :{key}")
                else:
                    update_parts.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value
            
            update_expression = "SET " + ", ".join(update_parts)
            
            update_params = {
                'Key': {
                    'PK': f"EVENT#{event_id}",
                    'SK': 'METADATA'
                },
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
    
    def delete(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            self.table.delete_item(
                Key={
                    'PK': f"EVENT#{event_id}",
                    'SK': 'METADATA'
                }
            )
            return True
        except ClientError as e:
            raise Exception(f"Error deleting event: {e.response['Error']['Message']}")
    
    def update_capacity(self, event_id: str, increment: int) -> Dict[str, Any]:
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
