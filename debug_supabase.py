import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Connecting to {url} with SERVICE_ROLE_KEY...")
supabase: Client = create_client(url, key)

# List of tables we expect
expected_tables = ["profiles", "users", "orders", "products", "woocommerce", "subscribers"]

print("\n--- Checking Table Access ---")
for table in expected_tables:
    try:
        # Try to fetch 1 row
        res = supabase.table(table).select("*").limit(1).execute()
        print(f"✅ Table '{table}': Accessible. (Rows returned: {len(res.data)})")
    except Exception as e:
        error_details = str(e)
        if "PGRST205" in error_details:
            print(f"❌ Table '{table}': Schema Cache Error (PGRST205). The API does not see this table yet.")
        elif "404" in error_details:
             print(f"❌ Table '{table}': Not Found (404).")
        else:
            print(f"❌ Table '{table}': Error - {error_details}")

print("\n--- Diagnosis ---")
print("If you see 'Schema Cache Error', it means the table exists in the DB but PostgREST hasn't updated.")
print("If you see 'Not Found' or other errors, the table might not be created in the 'public' schema.")
