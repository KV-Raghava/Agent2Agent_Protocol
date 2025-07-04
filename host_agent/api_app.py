"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, AsyncIterator, Optional
import asyncio
import traceback
from adk_agent.agent import root_agent as routing_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types
from pprint import pformat
import uuid

app = FastAPI(
    title="A2A Host Agent API",
    description="API for A2A Host Agent that can help with weather and Airbnb accommodation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global configuration
APP_NAME = "routing_app"
USER_ID = "default_user"
SESSION_ID = "default_session"

SESSION_SERVICE = InMemorySessionService()
ROUTING_AGENT_RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[dict]] = None
    tool_responses: Optional[List[dict]] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

async def get_response_from_agent(
    message: str,
) -> dict:
    """Get response from host agent."""
    try:
        events_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(role="user", parts=[types.Part(text=message)]),
        )

        tool_calls = []
        tool_responses = []
        final_response = ""

        async for event in events_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        tool_call = {
                            "name": part.function_call.name,
                            "arguments": part.function_call.model_dump(exclude_none=True)
                        }
                        tool_calls.append(tool_call)
                    elif part.function_response:
                        response_content = part.function_response.response
                        if (
                            isinstance(response_content, dict)
                            and "response" in response_content
                        ):
                            formatted_response_data = response_content["response"]
                        else:
                            formatted_response_data = response_content
                        
                        tool_response = {
                            "name": part.function_response.name,
                            "response": formatted_response_data
                        }
                        tool_responses.append(tool_response)
            
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = "".join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break

        return {
            "response": final_response,
            "tool_calls": tool_calls,
            "tool_responses": tool_responses
        }
    except Exception as e:
        print(f"Error in get_response_from_agent (Type: {type(e)}): {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize the ADK session on startup."""
    try:
        print("Creating ADK session...")
        await SESSION_SERVICE.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        print("ADK session created successfully.")
    except Exception as e:
        print(f"Error creating ADK session: {e}")
        traceback.print_exc()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="a2a-host-agent",
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "A2A Host Agent API",
        "description": "This assistant can help you to check weather and find Airbnb accommodation",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint to interact with the host agent.
    
    The agent can help with:
    - Weather information
    - Airbnb accommodation search
    - Travel planning
    """
    try:
        # Get response from agent using default session
        result = await get_response_from_agent(message=request.message)
        
        return ChatResponse(
            response=result["response"],
            tool_calls=result["tool_calls"],
            tool_responses=result["tool_responses"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint for real-time responses.
    Returns Server-Sent Events (SSE) for streaming responses.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate_stream():
        try:
            events_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=types.Content(role="user", parts=[types.Part(text=request.message)]),
            )

            async for event in events_iterator:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.function_call:
                            data = {
                                "type": "tool_call",
                                "name": part.function_call.name,
                                "arguments": part.function_call.model_dump(exclude_none=True)
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                        elif part.function_response:
                            response_content = part.function_response.response
                            if isinstance(response_content, dict) and "response" in response_content:
                                formatted_response_data = response_content["response"]
                            else:
                                formatted_response_data = response_content
                            
                            data = {
                                "type": "tool_response",
                                "name": part.function_response.name,
                                "response": formatted_response_data
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                
                if event.is_final_response():
                    final_response = ""
                    if event.content and event.content.parts:
                        final_response = "".join([p.text for p in event.content.parts if p.text])
                    elif event.actions and event.actions.escalate:
                        final_response = f"Agent escalated: {event.error_message or 'No specific message.'}"
                    
                    data = {
                        "type": "final_response",
                        "response": final_response
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    break
        except Exception as e:
            error_data = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
