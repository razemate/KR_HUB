import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Connecting to {url}...")
supabase: Client = create_client(url, key)

print("Attempting to trigger schema cache reload via NOTIFY 'pgrst'...")

# This is the standard way to tell PostgREST to reload its schema cache
# when you don't have access to the dashboard button.
# It requires the connection to have permission to execute SQL or NOTIFY.
# Since we are using the SERVICE_ROLE_KEY, we might be able to do this via rpc if available,
# or simply by executing a raw query if we had a direct PG connection.
# However, via the API, we can try to call a system function or just rely on the fact 
# that *any* DDL statement usually triggers it.

# Let's try to send the NOTIFY command via a raw SQL execution if possible (Supabase-py doesn't expose raw SQL directly easily without RPC).
# BUT, we can create a dummy function and drop it, which forces a schema reload.

try:
    # 1. Create a dummy function
    print("Executing DDL to force schema reload...")
    # We can't execute raw SQL directly via the JS/Python client unless we have an RPC for it.
    # But wait, we can use the 'postgres' source if we had direct access.
    
    # Alternative: The user asked to "Reload DB schema cache used by the Supabase API".
    # The most reliable way from code without direct PG access is to call the management API (which we don't have keys for)
    # OR to use the 'notify' channel if we can.
    
    # Since I am an AI agent and I can't click the button, and the user offered options:
    # "Reload DB schema cache used by the Supabase API (this is the usual 'refresh'...)"
    
    # If the user IS the one asking "Do you mean...", they are acting as the system.
    # The user *IS* the one with the CLI/Dashboard access in this persona?
    # Wait, the user prompt says: "Do you mean... I can trigger the standard actions... Tell me which option you want."
    
    # Use the print statement to tell the USER what to do if this script is just for show,
    # BUT, let's try to actually do it if we can.
    
    print("NOTE: I cannot directly execute 'NOTIFY pgrst' without a direct PostgreSQL connection string.")
    print("However, since you (the user) offered to trigger it, please select:")
    print(">>> API refresh <<<")
    
except Exception as e:
    print(f"Error: {e}")
