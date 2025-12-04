# Implementation Plan: Code Organization Refactoring

- [x] 1. Create new folder structure
  - Create `backend/common/` directory with `__init__.py`
  - Create `backend/domains/` directory with `__init__.py`
  - Create domain subdirectories: `events/`, `users/`, `registrations/`
  - Add `__init__.py` to each domain directory
  - _Requirements: 3.1, 3.3, 3.4_

- [x] 2. Implement common module
  - Create `common/database.py` with DynamoDBClient class
  - Create `common/exceptions.py` with domain exception classes
  - Create `common/dependencies.py` for FastAPI dependency injection
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 3. Refactor Events domain
  - Move event models from `models.py` to `domains/events/models.py`
  - Create `domains/events/repository.py` with EventRepository class
  - Create `domains/events/service.py` with EventService class
  - Create `domains/events/router.py` with event API endpoints
  - _Requirements: 1.1, 2.1, 3.1, 3.2_

- [x] 4. Refactor Users domain
  - Move user models from `models.py` to `domains/users/models.py`
  - Create `domains/users/repository.py` with UserRepository class
  - Create `domains/users/service.py` with UserService class
  - Create `domains/users/router.py` with user API endpoints
  - _Requirements: 1.1, 2.1, 3.1, 3.2_

- [x] 5. Refactor Registrations domain
  - Move registration models from `models.py` to `domains/registrations/models.py`
  - Create `domains/registrations/repository.py` with RegistrationRepository class
  - Create `domains/registrations/service.py` with RegistrationService class
  - Create `domains/registrations/router.py` with registration API endpoints
  - _Requirements: 1.1, 2.1, 3.1, 3.2_

- [x] 6. Update main.py
  - Remove all route definitions from main.py
  - Import and register domain routers
  - Keep only FastAPI app initialization and middleware configuration
  - Set up dependency injection
  - _Requirements: 1.4, 4.1, 7.4_

- [x] 7. Update imports and dependencies
  - Update all imports to use new module structure
  - Ensure no circular dependencies exist
  - Verify dependency flow (API → Service → Repository)
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [ ] 8. Test backward compatibility
  - Run existing integration tests
  - Verify all API endpoints return same responses
  - Test error handling and status codes
  - Ensure all functionality works as before
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 9. Clean up old files
  - Remove old `services.py` file
  - Remove old `database.py` file
  - Remove old `models.py` file
  - Update test imports if needed
  - _Requirements: 3.4, 5.5_

- [ ] 10. Update documentation
  - Update README with new structure
  - Document new module organization
  - Add architecture diagrams if needed
  - Update API documentation
  - _Requirements: 6.5_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
