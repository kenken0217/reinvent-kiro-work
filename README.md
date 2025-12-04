# Event Management API

A serverless event management system built with FastAPI, AWS Lambda, API Gateway, and DynamoDB.

## 🚀 Live API Endpoint

**Production URL:** `https://iqizhy9s16.execute-api.us-west-2.amazonaws.com/prod/`

## 📁 Project Structure

```
.
├── backend/              # FastAPI application
│   ├── main.py          # API endpoints and Lambda handler
│   ├── models.py        # Pydantic data models
│   ├── database.py      # DynamoDB client
│   └── requirements.txt # Python dependencies
├── infrastructure/       # AWS CDK infrastructure code
│   ├── app.py           # CDK app entry point
│   ├── stacks/          # CDK stack definitions
│   └── cdk.json         # CDK configuration
└── .kiro/               # Kiro IDE configuration
    └── settings/
        └── mcp.json     # MCP server configuration
```

## 📊 Event Schema

Events are stored in DynamoDB with the following properties:

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `eventId` | string | Unique identifier | Auto-generated UUID or provided |
| `title` | string | Event title | 1-200 characters |
| `description` | string | Event description | Min 1 character |
| `date` | string | Event date | Format: YYYY-MM-DD |
| `location` | string | Event location | Min 1 character |
| `capacity` | integer | Maximum capacity | Greater than 0 |
| `organizer` | string | Event organizer | Min 1 character |
| `status` | string | Event status | active, inactive, cancelled, completed |

## 🔌 API Endpoints

### Create Event
```http
POST /events
Content-Type: application/json

{
  "eventId": "optional-custom-id",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "location": "San Francisco",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "active"
}
```

### List All Events
```http
GET /events
```

### List Events by Status
```http
GET /events?status=active
```

### Get Specific Event
```http
GET /events/{eventId}
```

### Update Event
```http
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 600
}
```

### Delete Event
```http
DELETE /events/{eventId}
```

## 🛠️ Setup & Deployment

### Prerequisites

- Node.js 18+ (for AWS CDK)
- Python 3.11+
- Docker (for Lambda bundling)
- AWS CLI configured with credentials

### Install AWS CDK

```bash
npm install -g aws-cdk
```

### Install Python Dependencies

```bash
# Infrastructure dependencies
cd infrastructure
pip install -r requirements.txt

# Backend dependencies (for local development)
cd ../backend
pip install -r requirements.txt
```

### Deploy to AWS

```bash
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

The deployment will output your API endpoint URL.

## 💻 Local Development

Run the FastAPI application locally:

```bash
cd backend
export DYNAMODB_TABLE_NAME=EventsTable
uvicorn main:app --reload
```

Access the interactive API docs at: `http://localhost:8000/docs`

## 🧪 Testing Examples

### Using curl

```bash
# Create an event
curl -X POST https://iqizhy9s16.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "description": "Testing the API",
    "date": "2024-12-20",
    "location": "Online",
    "capacity": 100,
    "organizer": "Test Org",
    "status": "active"
  }'

# List all events
curl https://iqizhy9s16.execute-api.us-west-2.amazonaws.com/prod/events

# Filter by status
curl https://iqizhy9s16.execute-api.us-west-2.amazonaws.com/prod/events?status=active
```

## 🏗️ Architecture

- **API Gateway**: RESTful API endpoint with CORS enabled
- **AWS Lambda**: Serverless compute running FastAPI via Mangum
- **DynamoDB**: NoSQL database with on-demand billing
- **IAM**: Least-privilege access policies

## 🔒 Security Features

- CORS configured for web access
- Input validation with Pydantic
- DynamoDB reserved keyword handling
- Proper error handling and HTTP status codes

## 📚 Documentation

API documentation is available at:
- Interactive docs: `{API_URL}/docs`
- ReDoc: `{API_URL}/redoc`
- Generated docs: `backend/docs/`

## 🤝 Contributing

1. Make changes to the code
2. Test locally
3. Deploy to AWS: `cd infrastructure && cdk deploy`
4. Commit and push to GitHub

## 📝 Notes

- DynamoDB reserved keywords (`status`, `capacity`, `date`, `location`, `description`) are handled using ExpressionAttributeNames
- The API uses Pydantic v2 with the `pattern` parameter for regex validation
- Lambda function is bundled with dependencies using AWS CDK PythonFunction construct
