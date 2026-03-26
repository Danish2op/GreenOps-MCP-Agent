"""FastAPI wrapper to serve the ADK Agent as a cloud service.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from greenops_agent.agent import root_agent

app = FastAPI(title="GreenOps Cloud Agent")
session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Create or retrieve a session
        session = await session_service.create_session(
            state={}, app_name="greenops_app", user_id=request.user_id
        )
        
        runner = Runner(
            app_name="greenops_app",
            agent=root_agent,
            session_service=session_service,
        )
        
        content = types.Content(role="user", parts=[types.Part(text=request.message)])
        
        response_text = ""
        # Run the agent and collect the final text response
        async for event in runner.run_async(
            session_id=session.id, 
            user_id=request.user_id, 
            new_message=content
        ):
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
        
        return {"response": response_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
