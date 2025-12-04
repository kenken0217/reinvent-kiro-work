"""
User API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from common.database import DynamoDBClient
from common.dependencies import get_database
from common.exceptions import ConflictError
from .models import User, UserCreate
from .repository import UserRepository
from .service import UserService


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(db: DynamoDBClient = Depends(get_database)) -> UserService:
    """Dependency for user service"""
    repository = UserRepository(db)
    return UserService(repository)


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    try:
        user_data = user.model_dump()
        created_user = service.create_user(user_data)
        return created_user
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    try:
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
