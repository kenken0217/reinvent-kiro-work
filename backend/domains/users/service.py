"""
User service for business logic
"""
from typing import Optional, Dict, Any
from common.exceptions import NotFoundError
from .repository import UserRepository


class UserService:
    """Service for user business logic"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        return self.repository.create(user_data)
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.repository.get_by_id(user_id)
    
    def user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        return self.repository.exists(user_id)
