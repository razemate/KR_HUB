-- Enable RLS (this will deny access until policies are in place)
ALTER TABLE IF EXISTS public.subscribers ENABLE ROW LEVEL SECURITY;

-- Policy: allow authenticated users to SELECT (change to ownership-based policy if needed)
DO
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'subscribers' 
        AND policyname = 'authenticated_select_all_subscribers'
    ) THEN
        CREATE POLICY authenticated_select_all_subscribers ON public.subscribers FOR SELECT TO authenticated USING (true);
    END IF;
END;

-- Policy: allow authenticated users to INSERT
DO
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = 'subscribers' 
        AND policyname = 'authenticated_insert_subscribers'
    ) THEN
        CREATE POLICY authenticated_insert_subscribers ON public.subscribers FOR INSERT TO authenticated WITH CHECK (true);
    END IF;
END;

-- Explicit grant to authenticated (optional, safe)
GRANT SELECT ON TABLE public.subscribers TO authenticated;
