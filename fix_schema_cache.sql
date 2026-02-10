-- Fix Schema Cache and Permissions
-- Run this in your Supabase SQL Editor

-- 1. Reload the Schema Cache (The most critical fix for PGRST205)
NOTIFY pgrst, 'reload schema';

-- 2. Ensure the API role has access to the public schema
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

-- 3. Ensure the API role can read all tables (Optional but recommended for fixing 404s)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;

-- 4. Make sure future tables are also accessible
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon, authenticated, service_role;
