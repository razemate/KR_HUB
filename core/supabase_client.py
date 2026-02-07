from supabase import create_client, Client
from core.config_manager import config
from typing import Optional

url = config.get("SUPABASE_URL")
key = config.get("SUPABASE_SERVICE_ROLE_KEY")

supabase: Optional[Client] = create_client(url, key) if url and key else None
