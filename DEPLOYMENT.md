# Vercel Deployment Guide

## Prerequisites
- GitHub repository with this code pushed
- Vercel account connected to your GitHub
- Supabase project created and configured
- AI API keys (Gemini and/or OpenRouter)

## Steps to Deploy

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Setup Vercel deployment"
git push origin main
```

### 2. Configure Environment Variables in Vercel

Go to your Vercel project settings and add these environment variables:

| Variable | Value | Source |
|----------|-------|--------|
| `SUPABASE_URL` | Your Supabase URL | Supabase Dashboard > Settings > API |
| `SUPABASE_SERVICE_ROLE_KEY` | Your service role key | Supabase Dashboard > Settings > API |
| `GLOBAL_GEMINI_KEY` | Your Gemini API key | Google AI Studio |
| `GLOBAL_OPENAI_KEY` | Your OpenRouter API key | OpenRouter Dashboard |

**Finding Supabase Credentials:**
1. Go to https://supabase.com/dashboard
2. Open your project
3. Click Settings > API
4. Copy the project URL and service role key

### 3. Connect GitHub Repository
1. Go to vercel.com
2. Click "Add New..." > "Project"
3. Select your GitHub repository
4. Vercel should auto-detect the configuration from `vercel.json`

### 4. Deploy
Once environment variables are set, Vercel will automatically:
- Build the frontend with `npm run build`
- Deploy backend Python functions as serverless functions
- Configure API rewrites to route `/modules/*` and `/ai/*` to the backend

## Deployment Architecture

```
https://kr-hub.vercel.app/
├── Frontend (Static + Vite build)
│   └── /frontend/dist (served as static files)
└── Backend (Serverless Python Functions)
    └── /backend/api/index.py (FastAPI app)
        ├── /modules/chat-with-data/analyze
        └── /ai/run
```

## API Rewrites

All API calls from the frontend are rewritten to backend functions:
- `/modules/*` → `/backend/api/index.py`
- `/ai/*` → `/backend/api/index.py`

## Troubleshooting

### "Failed to fetch" Error
- Ensure backend environment variables are set in Vercel
- Check that `/modules/chat-with-data/analyze` endpoint returns proper SSE format
- Verify CORS headers are set to allow all origins

### Authentication Failures
- Verify `SUPABASE_SERVICE_ROLE_KEY` is correct
- Check that Supabase authentication is working

### Build Failures
- Check Vercel build logs: Vercel Dashboard > Project > Deployments
- Ensure `requirements.txt` has all Python dependencies
- Verify `frontend/package.json` build script exists

## Local Development

For local development with hot-reload:

```bash
# Terminal 1: Backend
cd /workspaces/KR_HUB
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

The frontend will proxy `/modules/*` and `/ai/*` to the backend automatically (see `frontend/vite.config.js`).

## Production vs Development

- **Production (Vercel)**: Uses relative paths (`/modules/...`) - Vercel rewrites handle routing
- **Development (Local)**: Uses relative paths - Vite proxy handles routing to `localhost:8000`
- **Environment variables**: Set in Vercel project settings (not in `.env` files)

## Important Notes

⚠️ **Never commit `.env` files with real keys!**
- `.env.local` and `.env.development` are in `.gitignore`
- Always set environment variables in Vercel dashboard
- Use `.env.example` to document what variables are needed
