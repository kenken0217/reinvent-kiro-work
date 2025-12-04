# Event Management API

This project contains a FastAPI backend for event management with AWS CDK infrastructure.

## Project Structure

- `backend/` - FastAPI application with CRUD operations for events
- `infrastructure/` - AWS CDK infrastructure code

## Event Schema

Events have the following properties:
- `eventId` (string) - Unique identifier (auto-generated)
- `title` (string) - Event title
- `description` (string) - Event description
- `date` (string) - Event date (format: YYYY-MM-DD)
- `location` (string) - Event location
- `capacity` (integer) - Maximum capacity
- `organizer` (string) - Event organizer
- `status` (string) - Event status (upcoming|ongoing|completed|cancelled)

## API Endpoints

- `POST /events` - Create a new event
- `GET /events` - List all events
- `GET /events/{eventId}` - Get a specific event
- `PUT /events/{eventId}` - Update an event
- `DELETE /events/{eventId}` - Delete an event

## Deployment

### Prerequisites

1. Install AWS CDK:
```bash
npm install -g aws-cdk
```

2. Install Python dependencies:
```bash
cd infrastructure
pip install -r requirements.txt
```

### Deploy to AWS

```bash
cd infrastructure
cdk bootstrap  # Only needed once per account/region
cdk deploy
```

The API endpoint URL will be displayed in the output.

## Local Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing

The API includes:
- Input validation using Pydantic models
- Error handling for all operations
- CORS configuration for web access
- DynamoDB integration for data persistence
