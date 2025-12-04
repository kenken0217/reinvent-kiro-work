---
inclusion: fileMatch
fileMatchPattern: '**/{main,api,routes,endpoints,views,controllers}*.{py,js,ts}'
---

# API Standards and Best Practices

This steering file provides guidelines for maintaining consistent REST API standards across the project.

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

#### Server Error Codes (5xx)
- **500 Internal Server Error**: Unexpected server errors
- **503 Service Unavailable**: Temporary unavailability

## JSON Response Format Standards

### Success Response Format

```json
{
  "data": { ... },
  "message": "Optional success message"
}
```

For single resources:
```json
{
  "id": "123",
  "name": "Resource Name",
  "createdAt": "2024-12-03T10:00:00Z"
}
```

For collections:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "pageSize": 20
}
```

### Error Response Format

Always return consistent error responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

## API Endpoint Naming Conventions

- Use plural nouns for collections: `/events`, `/users`
- Use kebab-case for multi-word resources: `/event-categories`
- Use path parameters for specific resources: `/events/{eventId}`
- Use query parameters for filtering: `/events?status=active`
- Avoid verbs in URLs (use HTTP methods instead)

## Request/Response Guidelines

### Request Body
- Always validate input using Pydantic models or similar
- Reject unknown fields or handle them explicitly
- Use clear field names (camelCase or snake_case consistently)

### Response Body
- Always include relevant data in responses
- For POST requests, return the created resource with 201
- For PUT/PATCH, return the updated resource
- For DELETE, return 204 No Content or 200 with confirmation message

## CORS Configuration

- Configure CORS appropriately for web access
- Specify allowed origins explicitly in production
- Allow necessary HTTP methods and headers

## Error Handling

- Catch and handle all exceptions appropriately
- Never expose internal error details to clients
- Log errors server-side for debugging
- Return user-friendly error messages

## Validation

- Validate all input data before processing
- Use type hints and validation libraries (Pydantic)
- Return 400 Bad Request for validation errors
- Include specific field-level error details

## Documentation

- Document all endpoints with clear descriptions
- Include request/response examples
- Specify required vs optional parameters
- Document possible error responses

## Implementation Checklist

When creating or modifying API endpoints:

1. ✅ Use appropriate HTTP method
2. ✅ Return correct status codes
3. ✅ Validate input with Pydantic models
4. ✅ Handle errors gracefully
5. ✅ Return consistent JSON format
6. ✅ Add proper CORS configuration
7. ✅ Document the endpoint
8. ✅ Test all success and error cases
