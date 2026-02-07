from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
import os

# Ensure the root directory is in sys.path so modules like 'core' and 'backend' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ai_gateway import run_ai
from backend.auth_manager import get_current_user
from backend.modules import chat_with_data # Explicit Import

app = FastAPI(title="Central AI Hub Backend")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Modules
app.include_router(chat_with_data.router)

class AIRequest(BaseModel):
    messages: List[Dict[str, str]]
    provider: str = "gemini"
    model: Optional[str] = None
    temperature: float = 0.7

@app.post("/ai/run")
async def run_ai_endpoint(request: AIRequest, user: Any = Depends(get_current_user)):
    """
    Single endpoint for AI execution.
    """
    # Extract user ID safely
    if isinstance(user, dict):
        user_id = user.get("id")
    else:
        user_id = user.id

    try:
        response = run_ai(
            user_id=user_id,
            messages=request.messages,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature
        )
        return {"response": response}
    except Exception as e:
        print(f"Error in /ai/run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Central AI Hub Backend is running"}
