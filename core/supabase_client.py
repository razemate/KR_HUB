from supabase import create_client, Client
from backend.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE
from typing import Optional

url = SUPABASE_URL
key = SUPABASE_SERVICE_ROLE

supabase: Optional[Client] = create_client(url, key) if url and key else None
