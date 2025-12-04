"""
User repository for data access
"""
from typing import Optional, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError
from common.database import DynamoDBClient
from common.exceptions import ConflictError


class UserRepository:
    """Repository for user data access"""
    
    def __init__(self, db_client: DynamoDBClient):
        self.db = db_client
        self.table = db_client.get_table()
    
    def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
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
                raise ConflictError(f"User with ID {user_id} already exists")
            raise Exception(f"Error creating user: {e.response['Error']['Message']}")
    
    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
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
    
    def exists(self, user_id: str) -> bool:
        """Check if user exists"""
        user = self.get_by_id(user_id)
        return user is not None
