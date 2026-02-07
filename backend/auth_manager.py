from fastapi import Header, HTTPException
from core.supabase_client import supabase

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # verify token using real Supabase Auth
        res = supabase.auth.get_user(token)
        if not res or not res.user:
             raise HTTPException(status_code=401, detail="Invalid Token")
        return res.user
    except Exception as e:
        # If authentication fails, we must fail. No mocks.
        raise HTTPException(status_code=401, detail=f"Authentication Failed: {str(e)}")
