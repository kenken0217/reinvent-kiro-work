"""
Database client initialization and configuration
"""
import boto3
import os
from typing import Optional


class DynamoDBClient:
    """Base DynamoDB client for table access"""
    
    def __init__(self, table_name: Optional[str] = None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.environ.get('DYNAMODB_TABLE_NAME', 'EventsTable')
        self._table = None
    
    @property
    def table(self):
        """Lazy load the DynamoDB table"""
        if self._table is None:
            self._table = self.dynamodb.Table(self.table_name)
        return self._table
    
    def get_table(self):
        """Get the DynamoDB table instance"""
        return self.table


# Global instance for dependency injection
_db_client_instance = None


def get_db_client() -> DynamoDBClient:
    """Get or create the global database client instance"""
    global _db_client_instance
    if _db_client_instance is None:
        _db_client_instance = DynamoDBClient()
    return _db_client_instance
