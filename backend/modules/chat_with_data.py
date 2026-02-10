from fastapi import APIRouter, Depends, UploadFile, File, Form
from backend.auth_manager import get_current_user
from core.supabase_client import supabase
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi import Request
from typing import Optional
import json

# Import the new Service
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/chat-with-data", tags=["chat-with-data"])

async def get_current_user_optional(request: Request):
    """Get current user if authenticated, otherwise return None"""
    authorization = request.headers.get("authorization")
    if not authorization:
        return None

    token = authorization.replace("Bearer ", "")
    try:
        from core.supabase_client import supabase
        if not supabase:
            return None
        res = supabase.auth.get_user(token)
        if res and res.user:
            return res.user
        return None
    except Exception:
        return None

@router.post("/analyze")
async def analyze(
    request: Request,
    question: str = Form(...),
    history: str = Form("[]"), # New field for chat history
    table_name: str = Form("profiles"),
    mode: str = Form("database"), # 'general' or 'database'
    file: UploadFile = File(None),
    user: Optional[object] = Depends(get_current_user_optional)
):
    # Handle both authenticated and unauthenticated users
    if user:
        user_id = user.id if not isinstance(user, dict) else user.get("id")
    else:
        user_id = "anonymous"

    # 1. Process File
    file_context, image_data = await ChatService.process_file(file)

    # Parse History
    try:
        chat_history = json.loads(history)
    except:
        chat_history = []

    # --- GENERAL MODE ---
    if mode == "general":
        # Construct messages with history
        final_messages = chat_history + [
            {"role": "user", "content": f"{file_context}\n\nQuestion: {question}"}
        ]
        
        # Use Service to generate stream
        return StreamingResponse(
            ChatService.generate_response_stream(user_id, final_messages, image_data),
            media_type="text/event-stream"
        )

    # --- DATABASE MODE (Default) ---
    
    if not supabase:
        return JSONResponse(
            status_code=503,
            content={"detail": "Database is not configured on the server."},
        )
    
    # 2. Select Table
    used_table = ChatService.select_table(question, table_name)

    # 3. Query Database
    db_context, columns = ChatService.query_database(used_table, question)
    
    # Construct Prompt with History
    # We put the Context in the *System* or *Last User Message*.
    # Ideally, history comes first, then the new question with attached context.
    
    context_block = f"""
    CONTEXT:
    - Table: {used_table}
    - Schema Columns: {columns}
    - Database Data Sample: {db_context}
    - File Content: {file_context}
    """
    
    final_messages = chat_history + [
        {"role": "user", "content": f"""
        {context_block}
        
        USER QUESTION: "{question}"
        
        INSTRUCTIONS:
        1. The user might have typos (e.g., "sers" instead of "users"). INFER their intent based on the available data.
        2. Do NOT ask for clarification unless absolutely impossible to answer.
        3. If the data provides a clear answer (e.g., a count), state it directly.
        4. If the user asks for "active subscribers" and you see "status: active" in the data, count them and answer.
        5. Be helpful, direct, and smart.
        """}
    ]
    
    # 4. Return Stream
    return StreamingResponse(
        ChatService.generate_response_stream(user_id, final_messages, image_data),
        media_type="text/event-stream"
    )
