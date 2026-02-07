import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)

tables_to_check = ["profiles", "users", "subscribers", "orders", "products", "woocommerce", "test_data"]

print(f"Checking access for tables in {url}...")

for table in tables_to_check:
    try:
        # Limit 0 just checks existence/permission without fetching data
        res = supabase.table(table).select("*").limit(1).execute()
        print(f"[OK] Table '{table}' found. Rows: {len(res.data)}")
    except Exception as e:
        msg = str(e)
        if "PGRST205" in msg:
            print(f"[MISSING] Table '{table}' not found in schema cache.")
        else:
            print(f"[ERROR] Table '{table}': {msg}")
