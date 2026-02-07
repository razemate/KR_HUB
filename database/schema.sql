-- Create profiles table
create table public.profiles (
  id uuid references auth.users not null primary key,
  role text check (role in ('developer', 'user')) default 'user',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create ai_settings table
create table public.ai_settings (
  id uuid default uuid_generate_v4() primary key,
  provider text check (provider in ('gemini', 'openai', 'openrouter', 'anthropic')),
  model text,
  use_global_key boolean default true,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create user_api_keys table
create table public.user_api_keys (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  provider text not null,
  encrypted_key text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Set up Row Level Security (RLS)
alter table public.profiles enable row level security;
alter table public.ai_settings enable row level security;
alter table public.user_api_keys enable row level security;

create policy "Public profiles are viewable by everyone." on public.profiles for select using (true);
create policy "Users can insert their own profile." on public.profiles for insert with check (auth.uid() = id);
create policy "Users can update own profile." on public.profiles for update using (auth.uid() = id);

create policy "Users can view own api keys." on public.user_api_keys for select using (auth.uid() = user_id);
create policy "Users can insert own api keys." on public.user_api_keys for insert with check (auth.uid() = user_id);
