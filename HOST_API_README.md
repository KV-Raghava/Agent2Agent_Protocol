# Host Agent API

The Host Agent now supports both Gradio UI and FastAPI REST endpoints. This document explains how to use the new API interface.

## API Endpoints

### Health Check
```bash
GET /health
```
Returns the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "service": "a2a-host-agent",
  "version": "1.0.0"
}
```

### Service Information
```bash
GET /
```
Returns service information and available endpoints.

### Chat Endpoint
```bash
POST /chat
```
Main endpoint for interacting with the host agent.

**Request Body:**
```json
{
  "message": "What's the weather like in New York?",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "response": "The current weather in New York is...",
  "session_id": "session-123",
  "user_id": "user-456",
  "tool_calls": [
    {
      "name": "weather_tool",
      "arguments": {...}
    }
  ],
  "tool_responses": [
    {
      "name": "weather_tool",
      "response": {...}
    }
  ]
}
```

### Streaming Chat Endpoint
```bash
POST /chat/stream
```
Returns streaming responses using Server-Sent Events (SSE).

## Deployment Options

### Option 1: API Mode (Default)
The host agent will run as a FastAPI service by default.

### Option 2: Gradio Mode
To run with the original Gradio interface, set the environment variable:
```yaml
env:
- name: API_MODE
  value: "gradio"
```

## Testing the API

### Prerequisites
1. Ensure all agents are deployed and running
2. Port forward the host agent service:
```bash
kubectl port-forward service/host-agent-service 8003:8083
```

### Using curl
```bash
# Health check
curl http://localhost:8003/health

# Service info
curl http://localhost:8003/

# Chat request
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What'\''s the weather in Tokyo?"}'
```

### Using the Test Script
```bash
# Run the comprehensive test script
python test_host_api.py
```

### Using Python requests
```python
import requests

# Simple chat request
response = requests.post(
    "http://localhost:8003/chat",
    json={"message": "Find me an Airbnb in Paris"}
)
print(response.json())
```

## Example API Calls

### Weather Query
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What'\''s the weather like in London today?"
  }'
```

### Airbnb Query
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find me accommodation in Barcelona for next week"
  }'
```

### Complex Travel Planning
```bash
curl -X POST http://localhost:8003/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I'\''m planning a trip to Rome. Can you check the weather and find me some places to stay?"
  }'
```

## API Documentation

Once the service is running, you can access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8003/docs`
- **ReDoc**: `http://localhost:8003/redoc`

## Integration Examples

### JavaScript/TypeScript
```javascript
async function chatWithAgent(message) {
  const response = await fetch('http://localhost:8003/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message })
  });
  
  const data = await response.json();
  return data.response;
}

// Usage
chatWithAgent("What's the weather in Paris?")
  .then(response => console.log(response));
```

### Python
```python
import requests

def chat_with_agent(message, session_id=None, user_id=None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    if user_id:
        payload["user_id"] = user_id
    
    response = requests.post(
        "http://localhost:8003/chat",
        json=payload
    )
    return response.json()

# Usage
result = chat_with_agent("Find me hotels in Tokyo")
print(result["response"])
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful request
- `400`: Bad request (invalid input)
- `500`: Internal server error

Error responses include details:
```json
{
  "detail": "Error description"
}
```

## Session Management

The API supports multiple users and sessions:
- If no `session_id` is provided, a default session is used
- If no `user_id` is provided, a default user is used
- Each user/session combination maintains separate conversation context

## Switching Between UI and API

### Current Deployment (API Mode)
```bash
# Rebuild and redeploy with API mode
cd host_agent
docker build -t host-agent:latest .
kind load docker-image host-agent:latest --name agents-cluster
kubectl delete pod -l app=host-agent  # Force restart with new image
```

### Switch to Gradio Mode
Update the deployment:
```yaml
env:
- name: API_MODE
  value: "gradio"
```

Then apply the changes:
```bash
kubectl apply -f host-agent.yaml
```
