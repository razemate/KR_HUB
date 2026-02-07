from supabase import create_client, Client
from core.config_manager import config

# Enforce real configuration. App will crash if missing.
url = config.get_required("SUPABASE_URL")
key = config.get_required("SUPABASE_SERVICE_ROLE_KEY")

# Initialize client directly. Let exceptions bubble up.
# This ensures we never run with a broken or mock database connection.
supabase: Client = create_client(url, key)
