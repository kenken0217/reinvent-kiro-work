# Design Document: User Registration System

## Overview

The User Registration System extends the existing Event Management API to support user management, event registration workflows, capacity management, and waitlist functionality. The system maintains the current FastAPI + DynamoDB architecture and adds new entities (Users, Registrations, Waitlists) with their corresponding API endpoints and database operations.

The design follows a RESTful API pattern with clear separation between API layer (FastAPI), business logic, and data persistence (DynamoDB). All operations maintain ACID properties through DynamoDB's transactional capabilities and conditional writes.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI App    │
│  (Lambda)       │
├─────────────────┤
│  - Users API    │
│  - Events API   │
│  - Registrations│
└────────┬────────┘
         │
┌────────▼────────┐
│  DynamoDB       │
│  Single Table   │
│  Design         │
└─────────────────┘
```

### Technology Stack

- **API Framework**: FastAPI (existing)
- **Runtime**: AWS Lambda with Mangum adapter (existing)
- **Database**: DynamoDB with single-table design
- **Validation**: Pydantic v2 models
- **Infrastructure**: AWS CDK (Python)

### Design Decisions

1. **Single Table Design**: Use DynamoDB single-table design pattern with composite keys to optimize for access patterns and reduce costs
2. **Optimistic Locking**: Use conditional writes with version attributes to handle concurrent registrations
3. **Atomic Operations**: Use DynamoDB transactions for operations that span multiple entities (e.g., registration + capacity update)
4. **Waitlist as Separate Items**: Store waitlist entries as separate items with sort keys for ordering

## Components and Interfaces

### 1. Data Models (Pydantic)

#### User Models
```python
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)

class User(BaseModel):
    userId: str
    name: str
    createdAt: str  # ISO 8601 timestamp
```

#### Event Models (Extended)
```python
class EventCreate(BaseModel):
    # Existing fields...
    capacity: int = Field(..., gt=0)
    waitlistEnabled: bool = Field(default=False)
    currentRegistrations: int = Field(default=0)

class Event(BaseModel):
    # Existing fields...
    capacity: int
    waitlistEnabled: bool
    currentRegistrations: int
    availableCapacity: int  # Computed field
```

#### Registration Models
```python
class RegistrationCreate(BaseModel):
    userId: str
    eventId: str

class Registration(BaseModel):
    registrationId: str
    userId: str
    eventId: str
    registeredAt: str  # ISO 8601 timestamp
    status: str  # "confirmed"

class WaitlistEntry(BaseModel):
    waitlistId: str
    userId: str
    eventId: str
    addedAt: str  # ISO 8601 timestamp
    position: int
```

### 2. API Endpoints

#### User Endpoints
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user details
- `GET /users/{user_id}/registrations` - List user's registered events

#### Registration Endpoints
- `POST /registrations` - Register user for an event
- `DELETE /registrations/{registration_id}` - Unregister from an event
- `GET /events/{event_id}/registrations` - List all registrations for an event
- `GET /events/{event_id}/waitlist` - Get waitlist for an event

### 3. Database Schema (DynamoDB Single Table)

#### Access Patterns
1. Get user by ID
2. Get event by ID
3. Get all registrations for a user
4. Get all registrations for an event
5. Check if user is registered for an event
6. Get waitlist for an event (ordered)
7. Get first person on waitlist

#### Table Design
```
Table: EventsTable (existing, extended)

Primary Key: PK (Partition Key), SK (Sort Key)

Item Types:

1. User
   PK: USER#{userId}
   SK: METADATA
   Attributes: userId, name, createdAt

2. Event (existing, extended)
   PK: EVENT#{eventId}
   SK: METADATA
   Attributes: eventId, title, description, date, location, 
               capacity, currentRegistrations, waitlistEnabled, 
               organizer, status, version

3. Registration
   PK: USER#{userId}
   SK: REG#{eventId}
   Attributes: registrationId, userId, eventId, registeredAt, status
   GSI1PK: EVENT#{eventId}
   GSI1SK: REG#{userId}

4. Waitlist Entry
   PK: EVENT#{eventId}
   SK: WAIT#{timestamp}#{userId}
   Attributes: waitlistId, userId, eventId, addedAt, position

GSI1 (Global Secondary Index):
- GSI1PK (Partition Key)
- GSI1SK (Sort Key)
- Purpose: Query registrations by event
```

### 4. Business Logic Layer

#### RegistrationService
```python
class RegistrationService:
    def register_user(self, user_id: str, event_id: str) -> Registration | WaitlistEntry
    def unregister_user(self, user_id: str, event_id: str) -> bool
    def get_user_registrations(self, user_id: str) -> List[Event]
    def promote_from_waitlist(self, event_id: str) -> Optional[Registration]
```

#### UserService
```python
class UserService:
    def create_user(self, user_data: UserCreate) -> User
    def get_user(self, user_id: str) -> Optional[User]
    def user_exists(self, user_id: str) -> bool
```

## Data Models

### Entity Relationships

```
User ──────< Registration >────── Event
                                    │
                                    │
                                    └──< WaitlistEntry >── User
```

### State Transitions

#### Registration Flow
```
User Request
    │
    ├─→ Event has capacity? ──Yes──→ Create Registration
    │                                 Update capacity
    │                                 Return Registration
    │
    └─→ No ──→ Waitlist enabled? ──Yes──→ Add to Waitlist
                                           Return WaitlistEntry
               │
               └─→ No ──→ Return Error (Event Full)
```

#### Unregistration Flow
```
User Unregister
    │
    ├─→ Remove Registration
    │   Increment capacity
    │
    └─→ Waitlist has entries? ──Yes──→ Get first entry
                                       Create Registration
                                       Remove from Waitlist
                                       Update capacity
        │
        └─→ No ──→ Done
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: User creation preserves attributes
*For any* valid user ID and name, creating a user and then retrieving it should return a user with the same ID and name.
**Validates: Requirements 1.1, 1.4**

### Property 2: Event creation preserves attributes
*For any* valid event data (name, capacity, waitlist setting), creating an event and then retrieving it should return an event with the same attributes.
**Validates: Requirements 2.1, 2.4**

### Property 3: Entity IDs remain stable
*For any* created entity (User or Event), retrieving it multiple times should always return the same identifier.
**Validates: Requirements 1.5, 2.5**

### Property 4: Waitlist initialization
*For any* event created with waitlist enabled, the waitlist should be empty immediately after creation.
**Validates: Requirements 2.2**

### Property 5: Registration decrements capacity
*For any* user and event with available capacity, successfully registering the user should decrement the event's available capacity by exactly 1.
**Validates: Requirements 3.1**

### Property 6: Registration persistence
*For any* successful registration, the registration should be retrievable and contain the correct user ID and event ID.
**Validates: Requirements 3.5**

### Property 7: Full event with waitlist adds to waitlist
*For any* event at full capacity with waitlist enabled, attempting to register a new user should add that user to the waitlist in order of request time.
**Validates: Requirements 4.1**

### Property 8: Waitlist maintains temporal ordering
*For any* sequence of users added to a waitlist, the waitlist order should match the chronological order of addition.
**Validates: Requirements 4.3**

### Property 9: Waitlist entry persistence
*For any* user added to a waitlist, the waitlist entry should be retrievable with correct user ID, event ID, and position.
**Validates: Requirements 4.5**

### Property 10: Unregistration increments capacity
*For any* registered user who unregisters from an event, the event's available capacity should increase by exactly 1.
**Validates: Requirements 5.1**

### Property 11: Waitlist promotion on unregistration
*For any* event with registrations at capacity and a non-empty waitlist, when a user unregisters, the first user on the waitlist should be automatically registered and removed from the waitlist.
**Validates: Requirements 5.2, 5.4**

### Property 12: User registrations query completeness
*For any* user registered for a set of events, querying their registrations should return exactly those events with all required details (event ID, name, capacity).
**Validates: Requirements 6.1, 6.4**

### Property 13: Registration query ordering consistency
*For any* user, querying their registrations multiple times should return the events in the same consistent order.
**Validates: Requirements 6.5**

### Property 14: Capacity never exceeded (Critical Invariant)
*For any* event at any point in time, the number of confirmed registrations should never exceed the event's capacity.
**Validates: Requirements 7.4**

### Property 15: Registration and capacity atomicity
*For any* registration or unregistration operation, the registration count and available capacity should always be consistent (registrations + available = total capacity).
**Validates: Requirements 7.2**

### Property 16: Waitlist promotion atomicity
*For any* waitlist promotion, a user should never appear in both the waitlist and registrations simultaneously.
**Validates: Requirements 7.3**

### Property 17: Referential integrity
*For any* registration, both the referenced user and event should exist in the system.
**Validates: Requirements 7.5**

### Property 18: Concurrent registration safety
*For any* set of concurrent registration requests for the same event, the system should process them such that capacity is never exceeded.
**Validates: Requirements 7.1**

## Error Handling

### Error Categories

1. **Validation Errors (400 Bad Request)**
   - Missing required fields
   - Invalid field formats
   - Capacity less than 1
   - Empty or invalid IDs

2. **Not Found Errors (404 Not Found)**
   - User does not exist
   - Event does not exist
   - Registration does not exist

3. **Conflict Errors (409 Conflict)**
   - Duplicate user ID
   - User already registered for event
   - User already on waitlist
   - User not registered (on unregister attempt)

4. **Capacity Errors (422 Unprocessable Entity)**
   - Event at full capacity (no waitlist)
   - Cannot reduce event capacity below current registrations

5. **Concurrency Errors (409 Conflict)**
   - Optimistic locking failure
   - Retry with exponential backoff

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "field": "fieldName"  // Optional, for validation errors
}
```

### Retry Strategy
- Use exponential backoff for concurrency conflicts
- Maximum 3 retry attempts
- Initial delay: 100ms, multiplier: 2

## Testing Strategy

### Unit Testing

The system will use **pytest** as the testing framework with the following structure:

```
backend/tests/
├── test_users.py           # User creation and retrieval tests
├── test_events.py          # Event management tests (extended)
├── test_registrations.py   # Registration workflow tests
├── test_waitlist.py        # Waitlist management tests
└── conftest.py            # Shared fixtures and test utilities
```

**Unit Test Coverage:**
- API endpoint validation and error handling
- Pydantic model validation
- Database client methods
- Edge cases:
  - Empty inputs
  - Duplicate IDs
  - Non-existent references
  - Boundary conditions (capacity = 1, capacity = 0 registrations)

**Test Fixtures:**
- Mock DynamoDB table
- Sample users, events, registrations
- Pre-populated test scenarios (full events, waitlists)

### Property-Based Testing

The system will use **Hypothesis** for property-based testing, configured to run a minimum of 100 iterations per property.

**Property Test Requirements:**
- Each property test MUST be tagged with a comment referencing the design document property
- Tag format: `# Feature: user-registration, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Tests should use smart generators that constrain to valid input spaces

**Test Generators:**
```python
# Example generators
@st.composite
def valid_user_id(draw):
    return draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters='\x00')))

@st.composite
def valid_event_with_capacity(draw):
    capacity = draw(st.integers(min_value=1, max_value=1000))
    current = draw(st.integers(min_value=0, max_value=capacity))
    return {
        'eventId': draw(st.uuids()).hex,
        'capacity': capacity,
        'currentRegistrations': current,
        'waitlistEnabled': draw(st.booleans())
    }
```

**Property Test Files:**
```
backend/tests/properties/
├── test_user_properties.py
├── test_event_properties.py
├── test_registration_properties.py
├── test_capacity_properties.py
└── test_concurrency_properties.py
```

### Integration Testing

- Test complete workflows end-to-end
- Use LocalStack or DynamoDB Local for integration tests
- Test scenarios:
  - User registers for event → verify in database
  - Event fills up → next user goes to waitlist
  - User unregisters → waitlist user promoted
  - Concurrent registrations → capacity respected

### Concurrency Testing

- Use threading or asyncio to simulate concurrent requests
- Verify capacity invariant holds under concurrent load
- Test optimistic locking behavior
- Verify no race conditions in waitlist promotion

## Implementation Notes

### DynamoDB Considerations

1. **Conditional Writes**: Use `ConditionExpression` to prevent race conditions
   ```python
   # Example: Only register if capacity available
   condition = 'currentRegistrations < capacity'
   ```

2. **Transactions**: Use `transact_write_items` for multi-item operations
   ```python
   # Example: Unregister + promote from waitlist
   transact_items = [
       {'Delete': {...}},  # Remove registration
       {'Put': {...}},     # Add new registration
       {'Delete': {...}},  # Remove from waitlist
       {'Update': {...}}   # Update capacity
   ]
   ```

3. **Version Attributes**: Add `version` field to events for optimistic locking
   ```python
   update_expression = 'SET currentRegistrations = :new, version = :new_version'
   condition_expression = 'version = :old_version'
   ```

### Performance Optimization

1. **Batch Operations**: Use `batch_get_item` for fetching multiple registrations
2. **Projection Expressions**: Only fetch needed attributes to reduce data transfer
3. **Caching**: Consider caching event capacity information for high-traffic events
4. **Indexes**: GSI1 enables efficient event-to-registrations queries

### Security Considerations

1. **Input Validation**: Pydantic models validate all inputs
2. **SQL Injection**: Not applicable (NoSQL database)
3. **Rate Limiting**: Implement at API Gateway level
4. **Authentication**: Add user authentication in future iteration
5. **Authorization**: Verify user can only unregister themselves

## Future Enhancements

1. **Email Notifications**: Notify users when promoted from waitlist
2. **Registration Limits**: Limit number of events per user
3. **Event Categories**: Add event categorization and filtering
4. **Waitlist Position**: Allow users to check their waitlist position
5. **Bulk Operations**: Support bulk registration/unregistration
6. **Audit Trail**: Track all registration changes for compliance
7. **Analytics**: Event popularity metrics and registration trends
