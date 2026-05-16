# Backend Deployment on Render

## Render service settings
- Root directory: backend
- Build command: pip install -r requirements.txt
- Start command: ./start.sh

## Required environment variables
- MONGO_URI: MongoDB connection string for the primary database.
- NEMOTRON_API_KEY: NVIDIA Nemotron API key for AI risk analysis and chat.
- NEMOTRON_BASE_URL: Base URL for Nemotron API (default is the NVIDIA NVCF endpoint).
- NVIDIA_API_KEY: API key used by the LangChain NVIDIA endpoint (if using ai_analyzer).
- FRONTEND_ORIGIN: Allowed frontend origin for CORS (for example, https://your-frontend.onrender.com).

## Optional environment variables
- ALLOWED_ORIGINS: Comma-separated list of additional allowed origins for CORS.
- PORT: Render supplies this automatically; local default is 8000.

## MongoDB Atlas network access
- Add Render outbound IPs to the Atlas network access list, or
- Temporarily allow access from anywhere (0.0.0.0/0) while testing.
