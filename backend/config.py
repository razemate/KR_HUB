import os
from dotenv import load_dotenv
load_dotenv()  # safe locally, ignored in Vercel

# Supabase
# Fallback to VITE_ prefixed variables if standard ones are missing (convenience for shared envs)
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")

# AI Providers (Backend Only - No VITE prefix)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
