# Central AI Hub

A centralized AI provider management hub with role-based access.

## Project Structure
- `backend/`: FastAPI backend with AI Gateway and Auth.
- `frontend/`: React + Vite frontend with Tailwind CSS.
- `core/`: Shared logic (Config, Role Guard).
- `database/`: SQL schemas for Supabase.

## Setup

### Prerequisites
1. Node.js & npm
2. Python 3.8+
3. Supabase Project

### Backend Setup
1. Open a terminal in the root directory.
2. `cd backend`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables in `.env` (copy from `.env.example`).
5. Run server: `uvicorn backend.main:app --reload`

### Frontend Setup
1. Open a terminal in the root directory.
2. `cd frontend`
3. Install dependencies: `npm install`
4. Run dev server: `npm run dev`

### Database Setup
1. Create a new Supabase project.
2. Go to the SQL Editor in Supabase.
3. Copy and run the contents of `database/schema.sql`.
4. Configure Authentication to use Email/Password or Google OAuth.

## Features
- **Role-Based Access**: Developer vs User views.
- **AI Gateway**: Centralized routing for Gemini, OpenAI, etc.
- **BYOK**: Bring Your Own Key support (encrypted in DB).
- **Modules**: Pluggable UI/Logic modules (Chat, Reports).
