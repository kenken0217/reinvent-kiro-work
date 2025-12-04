# Design Document: Code Organization Refactoring

## Overview

This design document outlines the refactoring of the Event Management API codebase to improve code organization, maintainability, and testability. The refactoring implements a clean architecture pattern with clear separation of concerns across three main layers: API (Controllers/Routers), Service (Business Logic), and Repository (Data Access).

The refactoring maintains 100% backward compatibility with existing API endpoints while reorganizing the internal code structure to follow domain-driven design principles.

## Architecture

### Current Structure
```
backend/
├── main.py              # All API endpoints + some business logic
├── services.py          # Business logic services
├── database.py          # All database operations
├── models.py            # All Pydantic models
└── requirements.txt
```

### Target Structure
```
backend/
├── main.py                    # FastAPI app initialization only
├── requirements.txt
├── common/                    # Shared utilities and base classes
│   ├── __init__.py
│   ├── database.py           # DynamoDB client initialization
│   ├── dependencies.py       # FastAPI dependency injection
│   └── exceptions.py         # Custom exception classes
├── domains/                   # Domain-specific code
│   ├── __init__.py
│   ├── events/               # Event domain
│   │   ├── __init__.py
│   │   ├── models.py         # Event Pydantic models
│   │   ├── repository.py     # Event data access
│   │   ├── service.py        # Event business logic
│   │   └── router.py         # Event API endpoints
│   ├── users/                # User domain
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   └── registrations/        # Registration domain
│       ├── __init__.py
│       ├── models.py
│       ├── repository.py
│       ├── service.py
│       └── router.py
└── tests/                    # Test files (existing)
    └── test_integration.py
```

## Components and Interfaces

### 1. Common Module

#### database.py
```python
class DynamoDBClient:
    """Base DynamoDB client for table access"""
    def __init__(self, table_name: str = None)
    def get_table(self) -> Table
```

#### dependencies.py
```python
def get_event_service() -> EventService
def get_user_service() -> UserService
def get_registration_service() -> RegistrationService
```

#### exceptions.py
```python
class DomainException(Exception): pass
class NotFoundError(DomainException): pass
class ConflictError(DomainException): pass
class ValidationError(DomainException): pass
class CapacityError(DomainException): pass
```

### 2. Domain Modules

Each domain follows the same structure:

#### models.py
- Pydantic models for request/response validation
- Domain-specific data transfer objects (DTOs)

#### repository.py
- Data access layer
- All DynamoDB operations for the domain
- Returns domain models or dictionaries

#### service.py
- Business logic layer
- Orchestrates operations between repositories
- Implements domain rules and workflows
- Raises domain exceptions

#### router.py
- FastAPI route definitions
- HTTP request/response handling
- Delegates to service layer
- Converts domain exceptions to HTTP responses

### 3. Layer Responsibilities

#### API Layer (router.py)
**Responsibilities:**
- Define FastAPI routes and HTTP methods
- Parse and validate HTTP requests
- Call service layer methods
- Format HTTP responses
- Convert domain exceptions to appropriate HTTP status codes
- Handle CORS and middleware concerns

**NOT Responsible For:**
- Business logic
- Data validation beyond HTTP concerns
- Direct database access
- Domain rules

#### Service Layer (service.py)
**Responsibilities:**
- Implement business logic and domain rules
- Orchestrate operations across repositories
- Validate business rules
- Manage transactions and consistency
- Raise domain-specific exceptions

**NOT Responsible For:**
- HTTP concerns (status codes, headers)
- Direct database operations
- Request/response formatting

#### Repository Layer (repository.py)
**Responsibilities:**
- Execute database queries
- Map between database records and domain models
- Handle database-specific errors
- Implement data access patterns
- Manage database connections

**NOT Responsible For:**
- Business logic
- HTTP concerns
- Cross-domain operations

## Data Models

### Model Organization

Each domain has its own models.py file containing:

1. **Request Models**: For API input validation
   - `EventCreate`, `EventUpdate`
   - `UserCreate`
   - `RegistrationCreate`

2. **Response Models**: For API output
   - `Event`, `EventList`
   - `User`, `UserList`
   - `Registration`, `WaitlistEntry`

3. **Internal Models**: For service layer (if needed)
   - Domain-specific DTOs

### Model Inheritance

```python
# Common base models (if needed)
class TimestampedModel(BaseModel):
    createdAt: str
    updatedAt: Optional[str] = None

# Domain models extend base
class Event(TimestampedModel):
    eventId: str
    title: str
    # ... other fields
```

## Dependency Flow

```
┌─────────────────────────────────────────┐
│           main.py (FastAPI App)         │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Events │  │ Users  │  │  Reg   │  ← API Routers
│ Router │  │ Router │  │ Router │
└───┬────┘  └───┬────┘  └───┬────┘
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Events │  │ Users  │  │  Reg   │  ← Services
│Service │  │Service │  │Service │
└───┬────┘  └───┬────┘  └───┬────┘
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Events │  │ Users  │  │  Reg   │  ← Repositories
│  Repo  │  │  Repo  │  │  Repo  │
└───┬────┘  └───┬────┘  └───┬────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │  DynamoDB      │
         │  Client        │
         └────────────────┘
```

## Error Handling

### Exception Hierarchy

```python
DomainException (base)
├── NotFoundError (404)
├── ConflictError (409)
├── ValidationError (400)
└── CapacityError (422)
```

### Error Handling Pattern

```python
# In router.py
@router.post("/events")
def create_event(event: EventCreate, service: EventService = Depends(get_event_service)):
    try:
        result = service.create_event(event)
        return result
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Dependency Injection

### FastAPI Dependencies

```python
# common/dependencies.py
def get_db_client() -> DynamoDBClient:
    return DynamoDBClient()

def get_event_repository(db: DynamoDBClient = Depends(get_db_client)) -> EventRepository:
    return EventRepository(db)

def get_event_service(repo: EventRepository = Depends(get_event_repository)) -> EventService:
    return EventService(repo)
```

### Usage in Routers

```python
# domains/events/router.py
@router.get("/events/{event_id}")
def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    return service.get_event(event_id)
```

## Migration Strategy

### Phase 1: Create New Structure
1. Create folder structure
2. Move models to domain folders
3. Create repository classes
4. Create service classes
5. Create router modules

### Phase 2: Update Dependencies
1. Update imports in main.py
2. Register routers with FastAPI app
3. Set up dependency injection

### Phase 3: Testing
1. Run existing integration tests
2. Verify all endpoints work
3. Test error handling
4. Validate response formats

### Phase 4: Cleanup
1. Remove old files (services.py, database.py)
2. Update documentation
3. Update imports in tests

## Testing Strategy

### Unit Testing

Each layer should be tested independently:

**Repository Tests:**
- Mock DynamoDB client
- Test CRUD operations
- Test error handling
- Test data mapping

**Service Tests:**
- Mock repositories
- Test business logic
- Test validation rules
- Test exception handling

**Router Tests:**
- Mock services
- Test HTTP request/response
- Test status codes
- Test error responses

### Integration Testing

- Use existing test_integration.py
- Test complete request flow
- Verify backward compatibility
- Test all API endpoints

## Implementation Notes

### Import Organization

```python
# Standard library
import os
from typing import Optional, List

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Local - common
from common.database import DynamoDBClient
from common.exceptions import NotFoundError

# Local - domain
from .models import Event, EventCreate
from .repository import EventRepository
from .service import EventService
```

### File Headers

Each file should include:
```python
"""
Module: domains.events.service
Description: Business logic for event management
"""
```

### Backward Compatibility

- All existing API endpoints must work unchanged
- Response formats must remain identical
- Error messages can be improved but status codes must match
- Query parameters and request bodies must be compatible

## Future Enhancements

1. **Add API versioning**: Support /v1/ and /v2/ endpoints
2. **Implement caching layer**: Add Redis for frequently accessed data
3. **Add event sourcing**: Track all changes to entities
4. **Implement CQRS**: Separate read and write models
5. **Add GraphQL API**: Provide alternative API interface
6. **Microservices**: Split domains into separate services

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: API endpoint preservation
*For any* existing API endpoint, calling it after refactoring should return the same response structure and status code as before refactoring.
**Validates: Requirements 4.1, 4.2, 4.5**

### Property 2: Layer isolation
*For any* API handler function, it should not contain direct database operations or business logic beyond calling service methods.
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 3: Repository encapsulation
*For any* service method that needs data, it should only access data through repository methods, never directly through database client.
**Validates: Requirements 2.1, 2.2, 2.5**

### Property 4: Domain cohesion
*For any* domain (events, users, registrations), all related code (models, repository, service, router) should be located in the same domain folder.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Dependency direction
*For any* module dependency, the dependency should flow from API → Service → Repository → Database, never in reverse.
**Validates: Requirements 8.2, 8.4, 8.5**

### Property 6: No circular dependencies
*For any* two modules A and B, if A imports B, then B should not import A directly or transitively.
**Validates: Requirements 8.1**

### Property 7: Consistent naming
*For any* repository class, it should be named `{Domain}Repository`, and for any service class, it should be named `{Domain}Service`.
**Validates: Requirements 6.1, 6.2, 6.5**

### Property 8: Shared code separation
*For any* functionality used by multiple domains, it should be located in the common module, not duplicated across domains.
**Validates: Requirements 5.1, 5.2, 5.5**
