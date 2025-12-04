import boto3
import os
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError

# DynamoDB reserved keywords that need expression attribute names
RESERVED_KEYWORDS = {'status', 'capacity', 'date', 'location', 'description'}

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

db_client = DynamoDBClient()
