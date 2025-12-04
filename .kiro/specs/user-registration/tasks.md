# Implementation Plan: User Registration System

- [ ] 1. Extend database schema and models
  - Update DynamoDB table design to support single-table pattern with composite keys
  - Add User, Registration, and WaitlistEntry Pydantic models
  - Update Event model to include waitlistEnabled and currentRegistrations fields
  - _Requirements: 1.1, 2.1, 2.2_

- [ ]* 1.1 Write property test for user creation
  - **Property 1: User creation preserves attributes**
  - **Validates: Requirements 1.1, 1.4**

- [ ]* 1.2 Write property test for event creation
  - **Property 2: Event creation preserves attributes**
  - **Validates: Requirements 2.1, 2.4**

- [ ]* 1.3 Write property test for entity ID stability
  - **Property 3: Entity IDs remain stable**
  - **Validates: Requirements 1.5, 2.5**

- [ ] 2. Implement User management functionality
  - Create UserService class with user creation and retrieval methods
  - Extend DynamoDBClient with user-related database operations
  - Implement user existence validation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 2.1 Write property test for waitlist initialization
  - **Property 4: Waitlist initialization**
  - **Validates: Requirements 2.2**

- [ ] 3. Implement User API endpoints
  - Add POST /users endpoint for user creation
  - Add GET /users/{user_id} endpoint for user retrieval
  - Add GET /users/{user_id}/registrations endpoint for listing user's events
  - Implement error handling for duplicate users and validation errors
  - _Requirements: 1.1, 1.2, 1.3, 6.1, 6.2, 6.3_

- [ ] 4. Extend Event functionality for registration support
  - Update Event model to track currentRegistrations and availableCapacity
  - Add waitlistEnabled field to event creation
  - Implement capacity validation logic
  - Update existing event endpoints to return new fields
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 5. Implement Registration service with capacity management
  - Create RegistrationService class
  - Implement register_user method with capacity checking
  - Implement atomic registration creation with capacity decrement using DynamoDB transactions
  - Add conditional writes to prevent race conditions
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.4_

- [ ]* 5.1 Write property test for registration capacity decrement
  - **Property 5: Registration decrements capacity**
  - **Validates: Requirements 3.1**

- [ ]* 5.2 Write property test for registration persistence
  - **Property 6: Registration persistence**
  - **Validates: Requirements 3.5**

- [ ]* 5.3 Write property test for capacity invariant
  - **Property 14: Capacity never exceeded (Critical Invariant)**
  - **Validates: Requirements 7.4**

- [ ]* 5.4 Write property test for registration atomicity
  - **Property 15: Registration and capacity atomicity**
  - **Validates: Requirements 7.2**

- [ ] 6. Implement Waitlist functionality
  - Implement waitlist addition logic when event is at capacity
  - Add waitlist ordering based on timestamp
  - Implement waitlist query methods
  - Add error handling for full events without waitlist
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 6.1 Write property test for waitlist addition
  - **Property 7: Full event with waitlist adds to waitlist**
  - **Validates: Requirements 4.1**

- [ ]* 6.2 Write property test for waitlist ordering
  - **Property 8: Waitlist maintains temporal ordering**
  - **Validates: Requirements 4.3**

- [ ]* 6.3 Write property test for waitlist persistence
  - **Property 9: Waitlist entry persistence**
  - **Validates: Requirements 4.5**

- [ ] 7. Implement unregistration with waitlist promotion
  - Implement unregister_user method in RegistrationService
  - Add automatic waitlist promotion logic
  - Use DynamoDB transactions for atomic unregister + promote operations
  - Implement promote_from_waitlist helper method
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 7.3_

- [ ]* 7.1 Write property test for unregistration capacity increment
  - **Property 10: Unregistration increments capacity**
  - **Validates: Requirements 5.1**

- [ ]* 7.2 Write property test for waitlist promotion
  - **Property 11: Waitlist promotion on unregistration**
  - **Validates: Requirements 5.2, 5.4**

- [ ]* 7.3 Write property test for waitlist promotion atomicity
  - **Property 16: Waitlist promotion atomicity**
  - **Validates: Requirements 7.3**

- [ ] 8. Implement Registration API endpoints
  - Add POST /registrations endpoint for user registration
  - Add DELETE /registrations/{registration_id} endpoint for unregistration
  - Add GET /events/{event_id}/registrations endpoint
  - Add GET /events/{event_id}/waitlist endpoint
  - Implement comprehensive error handling
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3_

- [ ]* 8.1 Write property test for user registrations query
  - **Property 12: User registrations query completeness**
  - **Validates: Requirements 6.1, 6.4**

- [ ]* 8.2 Write property test for query ordering consistency
  - **Property 13: Registration query ordering consistency**
  - **Validates: Requirements 6.5**

- [ ]* 8.3 Write property test for referential integrity
  - **Property 17: Referential integrity**
  - **Validates: Requirements 7.5**

- [ ] 9. Implement optimistic locking for concurrency control
  - Add version field to Event model
  - Implement version checking in registration operations
  - Add retry logic with exponential backoff
  - Handle concurrency conflicts gracefully
  - _Requirements: 7.1, 7.2_

- [ ]* 9.1 Write property test for concurrent registration safety
  - **Property 18: Concurrent registration safety**
  - **Validates: Requirements 7.1**

- [ ] 10. Update CDK infrastructure
  - Update DynamoDB table definition to include GSI1 for event-to-registrations queries
  - Add necessary IAM permissions for new operations
  - Update Lambda environment variables if needed
  - _Requirements: All (infrastructure support)_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
