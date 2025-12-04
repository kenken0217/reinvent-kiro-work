---
inclusion: fileMatch
fileMatchPattern: '**/{main,api,routes,endpoints,views,controllers}*.{py,js,ts}'
---

# API Standards and Best Practices

This steering file provides comprehensive guidelines for maintaining consistent REST API standards across the project.

## REST API Conventions

### HTTP Methods

Use appropriate HTTP methods for each operation:

- **GET**: Retrieve resources (read-only, idempotent)
- **POST**: Create new resources
- **PUT**: Update entire resources (replace)
- **PATCH**: Partially update resources
- **DELETE**: Remove resources

### HTTP Status Codes

Use standard HTTP status codes consistently:

#### Success Codes (2xx)
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful DELETE with no response body

#### Client Error Codes (4xx)
- **400 Bad Request**: Invalid input, validation errors
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity**: Validation errors with details
- **429 Too Many Requests**: Rate limit exceeded

#### Server Error Codes (5xx)
- **500 Internal Server Error**: Unexpected server errors
- **503 Service Unavailable**: Temporary unavailability

## Authentication and Authorization

### Authentication Methods

Support standard authentication mechanisms:

#### Bearer Token (JWT)
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### API Key
```http
X-API-Key: your-api-key-here
```

#### Basic Auth (for internal/admin endpoints only)
```http
Authorization: Basic base64(username:password)
```

### Authentication Response Codes

- **401 Unauthorized**: Missing or invalid authentication credentials
  ```json
  {
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Authentication required. Please provide valid credentials."
    }
  }
  ```

- **403 Forbidden**: Valid authentication but insufficient permissions
  ```json
  {
    "error": {
      "code": "FORBIDDEN",
      "message": "You do not have permission to access this resource."
    }
  }
  ```

### Token Expiration
- Include token expiration in authentication responses
- Return 401 with specific error code for expired tokens
  ```json
  {
    "error": {
      "code": "TOKEN_EXPIRED",
      "message": "Your authentication token has expired. Please login again."
    }
  }
  ```

## API Versioning

### URL Path Versioning (Recommended)
```
/v1/resources
/v2/resources
```

### Header Versioning (Alternative)
```http
Accept: application/vnd.api+json; version=1
```

### Version Strategy
- Use major version numbers only (v1, v2, v3)
- Maintain backward compatibility within major versions
- Deprecate old versions with sufficient notice (see Deprecation Strategy)

## JSON Response Format Standards

### Consistent Response Structure

**Always use this format for all responses:**

```json
{
  "id": "resource-id",
  "field1": "value1",
  "field2": "value2",
  "createdAt": "2024-12-03T10:00:00Z",
  "updatedAt": "2024-12-03T12:30:00Z"
}
```

**For collections with pagination:**

```json
{
  "items": [
    {
      "id": "1",
      "name": "Item 1"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

### Error Response Format

Always return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ],
    "timestamp": "2024-12-03T10:00:00Z",
    "path": "/v1/users",
    "requestId": "req-123-456"
  }
}
```

## Timestamp Format

### ISO 8601 with UTC

**Always use ISO 8601 format in UTC timezone:**

```json
{
  "createdAt": "2024-12-03T10:00:00Z",
  "updatedAt": "2024-12-03T12:30:00.123Z"
}
```

**Rules:**
- Always include timezone indicator (Z for UTC)
- Use UTC for all timestamps
- Include milliseconds for precision when needed
- Never use local timezones in API responses

## Pagination

### Offset-Based Pagination (Default)

**Query Parameters:**
```
GET /resources?page=1&pageSize=20
```

**Response:**
```json
{
  "items": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

**Constraints:**
- Default page size: 20
- Maximum page size: 100
- Minimum page size: 1

### Cursor-Based Pagination (For Large Datasets)

**Query Parameters:**
```
GET /resources?cursor=eyJpZCI6MTIzfQ&limit=20
```

**Response:**
```json
{
  "items": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTQzfQ",
    "previousCursor": "eyJpZCI6MTAzfQ",
    "hasNext": true,
    "hasPrevious": true
  }
}
```

## Filtering and Sorting

### Filtering

**Single field filter:**
```
GET /resources?status=active
GET /resources?createdAfter=2024-01-01
```

**Multiple filters (AND logic):**
```
GET /resources?status=active&category=tech&minPrice=100
```

**Comparison operators:**
```
GET /resources?price[gte]=100&price[lte]=500
GET /resources?createdAt[gt]=2024-01-01
```

**Operators:**
- `eq` or no operator: equals
- `ne`: not equals
- `gt`: greater than
- `gte`: greater than or equal
- `lt`: less than
- `lte`: less than or equal
- `in`: in array (comma-separated)

### Sorting

**Single field:**
```
GET /resources?sort=createdAt
GET /resources?sort=-createdAt  (descending)
```

**Multiple fields:**
```
GET /resources?sort=status,-createdAt
```

**Rules:**
- Prefix with `-` for descending order
- Default order is ascending
- Comma-separated for multiple fields

## Rate Limiting

### Rate Limit Headers

Include these headers in all responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
```

### Rate Limit Response (429)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 60
  }
}
```

### Rate Limit Strategy

- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Premium users**: 5000 requests/hour
- Use sliding window algorithm
- Return 429 status code when exceeded

## API Endpoint Examples

### POST - Create Resource

**Request:**
```http
POST /v1/users
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_123456",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2024-12-03T10:00:00Z",
  "updatedAt": "2024-12-03T10:00:00Z"
}
```

### GET - Retrieve Single Resource

**Request:**
```http
GET /v1/users/usr_123456
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "usr_123456",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "createdAt": "2024-12-03T10:00:00Z",
  "updatedAt": "2024-12-03T10:00:00Z"
}
```

### GET - List Resources with Filters

**Request:**
```http
GET /v1/users?role=admin&sort=-createdAt&page=1&pageSize=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "usr_123456",
      "email": "admin@example.com",
      "name": "Admin User",
      "role": "admin",
      "createdAt": "2024-12-03T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "pageSize": 20,
    "totalPages": 1,
    "hasNext": false,
    "hasPrevious": false
  }
}
```

### PUT - Update Resource

**Request:**
```http
PUT /v1/users/usr_123456
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Smith",
  "role": "admin"
}
```

**Response (200 OK):**
```json
{
  "id": "usr_123456",
  "email": "user@example.com",
  "name": "John Smith",
  "role": "admin",
  "createdAt": "2024-12-03T10:00:00Z",
  "updatedAt": "2024-12-03T15:30:00Z"
}
```

### DELETE - Remove Resource

**Request:**
```http
DELETE /v1/users/usr_123456
Authorization: Bearer <token>
```

**Response (204 No Content):**
```
(empty body)
```

### GET - Nested Resources

**Request:**
```http
GET /v1/users/usr_123456/orders?status=completed
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "ord_789",
      "userId": "usr_123456",
      "status": "completed",
      "total": 99.99,
      "createdAt": "2024-12-01T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 10,
    "page": 1,
    "pageSize": 20
  }
}
```

## Deprecation Strategy

### Deprecation Headers

When deprecating an endpoint:

```http
Deprecation: true
Sunset: Sat, 31 Dec 2024 23:59:59 GMT
Link: <https://api.example.com/v2/resources>; rel="alternate"
```

### Deprecation Timeline

1. **Announcement (T-6 months)**: Announce deprecation in release notes
2. **Warning Headers (T-3 months)**: Add deprecation headers to responses
3. **Documentation Update (T-3 months)**: Mark as deprecated in docs
4. **Sunset (T)**: Remove endpoint or version

### Deprecation Response

```json
{
  "data": {...},
  "warnings": [
    {
      "code": "DEPRECATED",
      "message": "This endpoint is deprecated and will be removed on 2024-12-31",
      "alternativeUrl": "/v2/resources"
    }
  ]
}
```

## Testing Guidelines

### Test Coverage Requirements

**Unit Tests:**
- All business logic functions
- Input validation
- Error handling
- Edge cases

**Integration Tests:**
- Complete request/response cycles
- Database interactions
- Authentication/authorization
- Error scenarios

**Test Structure:**
```python
def test_create_resource_success():
    """Test successful resource creation"""
    # Arrange
    payload = {"name": "Test"}
    
    # Act
    response = client.post("/v1/resources", json=payload)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
    assert "id" in response.json()
    assert "createdAt" in response.json()

def test_create_resource_validation_error():
    """Test validation error handling"""
    # Arrange
    payload = {"name": ""}  # Invalid
    
    # Act
    response = client.post("/v1/resources", json=payload)
    
    # Assert
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
```

### Test Scenarios to Cover

1. ✅ Successful operations (200, 201, 204)
2. ✅ Validation errors (400, 422)
3. ✅ Authentication errors (401)
4. ✅ Authorization errors (403)
5. ✅ Not found errors (404)
6. ✅ Conflict errors (409)
7. ✅ Rate limiting (429)
8. ✅ Server errors (500)
9. ✅ Pagination edge cases
10. ✅ Filtering and sorting

## Implementation Checklist

When creating or modifying API endpoints:

1. ✅ Use appropriate HTTP method
2. ✅ Return correct status codes
3. ✅ Implement authentication/authorization
4. ✅ Validate input with proper models
5. ✅ Handle errors gracefully with consistent format
6. ✅ Return consistent JSON response structure
7. ✅ Use ISO 8601 UTC timestamps
8. ✅ Implement pagination for collections
9. ✅ Support filtering and sorting
10. ✅ Add rate limiting headers
11. ✅ Include API versioning
12. ✅ Add proper CORS configuration
13. ✅ Document the endpoint with examples
14. ✅ Write comprehensive tests
15. ✅ Handle deprecation properly if updating existing endpoints
