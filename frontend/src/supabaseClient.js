import { createClient } from '@supabase/supabase-js'

// Hardcoded fallback for now based on project context, or we can use import.meta.env
// Ideally we use import.meta.env.VITE_SUPABASE_URL but let's ensure it works first.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://invhetvtoqibaogwodrx.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImludmhldHZ0b3FpYmFvZ3dvZHJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg4ODQ2MTUsImV4cCI6MjA4NDQ2MDYxNX0.so3Mf7ldrRH-colaPcU7R0nnTVX9wSRftzfUI3gAxsU'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
