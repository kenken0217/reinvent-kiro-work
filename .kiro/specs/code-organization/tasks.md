# Implementation Plan: Code Organization Refactoring

- [ ] 1. Create new folder structure
  - Create `backend/common/` directory with `__init__.py`
  - Create `backend/domains/` directory with `__init__.py`
  - Create `backend/domains/events/` directory with `__init__.py`
  - Create `backend/domains/users/` directory with `__init__.py`
  - Create `backend/domains/registrations/` directory with `__init__.py`
  - _Requirements: 3.1, 3.3, 3.4_

- [ ] 2. Create common module components
  - Create `backend/common/database.py` with DynamoDBClient base class
  - Create `backend/common/exceptions.py` with domain exception classes
  - Create `backend/common/dependencies.py` for FastAPI dependency injection
  - Move shared utilities and helpers to common module
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 3. Refactor Events domain
  - Create `backend/domains/events/models.py` and move Event models from `backend/models.py`
  - Create `backend/domains/events/repository.py` with EventRepository class
  - Extract event-related database operations from `backend/database.py` to EventRepository
  - Create `backend/domains/events/service.py` with EventService class
  - Move event business logic from `backend/services.py` to EventService
  - Create `backend/domains/events/router.py` with event API endpoints
  - Move event endpoints from `backend/main.py` to events router
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.2_

- [ ] 4. Refactor Users domain
  - Create `backend/domains/users/models.py` and move User models from `backend/models.py`
  - Create `backend/domains/users/repository.py` with UserRepository class
  - Extract user-related database operations from `backend/database.py` to UserRepository
  - Create `backend/domains/users/service.py` with UserService class
  - Move user business logic from `backend/services.py` to UserService
  - Create `backend/domains/users/router.py` with user API endpoints
  - Move user endpoints from `backend/main.py` to users router
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.2_

- [ ] 5. Refactor Registrations domain
  - Create `backend/domains/registrations/models.py` and move Registration/Waitlist models
  - Create `backend/domains/registrations/repository.py` with RegistrationRepository class
  - Extract registration-related database operations to RegistrationRepository
  - Create `backend/domains/registrations/service.py` with RegistrationService class
  - Move registration business logic from `backend/services.py` to RegistrationService
  - Create `backend/domains/registrations/router.py` with registration API endpoints
  - Move registration endpoints from `backend/main.py` to registrations router
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.2_

- [ ] 6. Implement dependency injection
  - Implement `get_db_client()` in `backend/common/dependencies.py`
  - Implement `get_event_repository()` and `get_event_service()` dependencies
  - Implement `get_user_repository()` and `get_user_service()` dependencies
  - Implement `get_registration_repository()` and `get_registration_service()` dependencies
  - Update all router functions to use FastAPI Depends() for dependency injection
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [ ] 7. Update main.py
  - Remove all endpoint definitions from `backend/main.py`
  - Keep only FastAPI app initialization and CORS configuration
  - Import and register event router with `app.include_router()`
  - Import and register user router with `app.include_router()`
  - Import and register registration router with `app.include_router()`
  - Keep root ("/") and health check endpoints in main.py
  - _Requirements: 1.4, 4.1, 8.4_

- [ ] 8. Update error handling
  - Implement domain exception classes in `backend/common/exceptions.py`
  - Update services to raise domain exceptions instead of generic Exception
  - Update routers to catch domain exceptions and convert to HTTP exceptions
  - Ensure error messages and status codes match original implementation
  - _Requirements: 4.3, 4.5_

- [ ] 9. Verify backward compatibility
  - Run existing integration tests without modification
  - Verify all API endpoints return same response formats
  - Test all CRUD operations for events, users, and registrations
  - Verify error handling and status codes match original behavior
  - Test query parameters and filtering functionality
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 10. Clean up old files
  - Remove `backend/services.py` (logic moved to domain services)
  - Remove `backend/database.py` (split into repositories)
  - Remove `backend/models.py` (split into domain models)
  - Update any remaining imports in test files
  - _Requirements: 3.3, 8.1_

- [ ] 11. Update documentation
  - Update README.md with new project structure
  - Add docstrings to all new modules explaining their purpose
  - Document dependency injection pattern
  - Update API documentation if needed
  - _Requirements: 6.5_

- [ ] 12. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
