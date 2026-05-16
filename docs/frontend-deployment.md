# Frontend Deployment on Vercel

## Vercel project settings
- Framework: Next.js
- Root directory: frontend
- Build command: npm run build
- Output: Next.js default

## Environment variables
Set these in the Vercel project settings (Settings -> Environment Variables):

Required:
- NEXT_PUBLIC_API_URL: Base URL for the backend API (for example, https://your-backend.onrender.com).

Notes:
- Vercel exposes variables prefixed with NEXT_PUBLIC_ to the browser.
- Redeploy after updating environment variables.
