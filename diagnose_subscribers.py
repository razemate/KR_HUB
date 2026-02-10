import os
import json
from supabase import create_client, Client
from backend.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE

# Configuration
SUPABASE_KEY = SUPABASE_SERVICE_ROLE 

# Let's try to connect
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Response Structure
response = {
    "status": "",
    "message": "",
    "details": {},
}

TABLE_NAME = "subscribers"

def generate_troubleshooting_sql():
    return [
        {
            "action": "Check table existence",
            "sql": f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{TABLE_NAME}';"
        },
        {
            "action": "Check columns",
            "sql": f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='{TABLE_NAME}';"
        },
        {
            "action": "Enable RLS and Policy (Safe Default)",
            "sql": f"""ALTER TABLE public.{TABLE_NAME} ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON public.{TABLE_NAME} FOR SELECT USING (true);
-- Optional: Allow inserts
CREATE POLICY "Enable insert for authenticated users only" ON public.{TABLE_NAME} FOR INSERT TO authenticated WITH CHECK (true);"""
        },
        {
            "action": "Reset Schema Cache (Fixes PGRST205)",
            "sql": "NOTIFY pgrst, 'reload schema';"
        },
        {
            "action": "Ensure Public Schema Access",
            "sql": "GRANT USAGE ON SCHEMA public TO anon, authenticated;"
        }
    ]

def generate_example_code():
    return {
        "supabase_js": f"""
import {{ createClient }} from '@supabase/supabase-js'

const supabaseUrl = '{SUPABASE_URL}'
const supabaseKey = 'SUPABASE_ANON_KEY' // Replace with your actual Anon Key
const supabase = createClient(supabaseUrl, supabaseKey)

async function fetchSubscribers() {{
  const {{ data, error }} = await supabase
    .from('{TABLE_NAME}')
    .select('*')
  
  if (error) console.error('Error:', error)
  else console.log('Subscribers:', data)
}}

fetchSubscribers()
""",
        "curl": f"""
curl -X GET '{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*' \\
  -H "apikey: SUPABASE_ANON_KEY" \\
  -H "Authorization: Bearer SUPABASE_ANON_KEY" \\
  -H "Content-Type: application/json" \\
  -H "Prefer: return=representation"
"""
    }

try:
    # 1. Attempt to fetch data
    # We fetch a small batch first to check existence and structure
    res = supabase.table(TABLE_NAME).select("*").limit(10).execute()
    
    data = res.data
    
    # 2. Analyze Success
    if data is not None:
        # Check for 'status' column
        has_status = False
        if len(data) > 0:
            # Case-insensitive check for 'status' column
            keys = [k.lower() for k in data[0].keys()]
            if "status" in keys:
                has_status = True
            else:
                response["details"]["warning"] = "Column 'status' not found in the first 10 rows."
        
        # Get Counts
        # Total count
        count_res = supabase.table(TABLE_NAME).select("*", count="exact", head=True).execute()
        total_count = count_res.count
        
        # Active count (if status exists)
        active_count = 0
        if has_status or len(data) == 0: 
            try:
                # Try fetching rows where status is 'active' (case-insensitive)
                active_res = supabase.table(TABLE_NAME).select("*", count="exact", head=True).ilike("status", "active").execute()
                active_count = active_res.count
            except:
                active_count = "Unknown (Status column missing or query failed)"

        response["status"] = "ok"
        response["message"] = f"Table '{TABLE_NAME}' is accessible."
        response["counts"] = {
            "total_rows": total_count,
            "active_rows": active_count
        }
        response["sample_rows"] = data
        
    else:
        raise Exception("No data returned (None)")

except Exception as e:
    error_str = str(e)
    response["status"] = "error"
    response["message"] = f"Failed to access table '{TABLE_NAME}'"
    
    # Analyze Error Code
    if "PGRST205" in error_str:
        response["details"]["error_code"] = "PGRST205"
        response["details"]["diagnosis"] = "Schema Cache Stale or Table Missing. PostgREST does not know this table exists."
    elif "404" in error_str:
        response["details"]["error_code"] = "404"
        response["details"]["diagnosis"] = "Endpoint not found. Check URL or table name."
    elif "permission denied" in error_str.lower():
        response["details"]["error_code"] = "403"
        response["details"]["diagnosis"] = "Permission Denied. RLS policies may be blocking access."
    else:
        response["details"]["raw_error"] = error_str

    response["troubleshooting_steps"] = generate_troubleshooting_sql()

# Always include example code
response["example_code"] = generate_example_code()

# Output JSON
print(json.dumps(response, indent=2))
