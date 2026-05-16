# Self-Defending GPT

## Objective
A secure, self-monitoring Generative AI system capable of detecting, mitigating, and logging adversarial attacks (like prompt injection, jailbreaking, and data extraction) in real-time, while providing actionable analytics through a security dashboard.

## Features
- **Real-Time Attack Detection**: Inspects incoming prompts for malicious intent using a zero-trust model.
- **Dynamic Mitigation**: Warns or blocks users based on risk scores and trust levels.
- **Security Dashboard**: Visualizes threats, risks, and user analytics using Recharts.
- **Detailed Logging**: Records all interactions in MongoDB with classifications and risk scores.
- **Resilient Architecture**: Containerized backend and frontend with scalable design.

## Architecture
The complete system architecture, including backend/frontend design, security pipeline, data models, and deployment strategy is documented in [docs/architecture.md](docs/architecture.md).

## Tech Stack
- **Frontend**: Next.js (React), Tailwind CSS, Recharts
- **Backend**: FastAPI (Python), LlamaGuard (via NVIDIA NIM / API), Groq API (for inference)
- **Database**: MongoDB (Atlas)
- **Deployment**: Render (Backend), Vercel (Frontend), Docker (Local)

## Setup Instructions

### Prerequisites
- Docker & Docker Compose installed
- MongoDB Atlas cluster set up
- NVIDIA API Key & Groq API Key
- Node.js & npm (for local non-docker development)
- Python 3.10+ (for local non-docker development)

### Local Docker Setup
1. Clone the repository.
2. Create a `.env` file in the repository root with the required secrets (do NOT commit it):

```env
MONGO_URI=your_mongo_uri
NVIDIA_API_KEY=your_nvidia_api_key
GROQ_API_KEY=your_groq_api_key
ALLOWED_ORIGINS=http://localhost:3000
```

3. Run locally with Docker Compose:

```bash
# build and run in foreground
docker compose up --build

# build and run detached
docker compose up -d --build

# stop and remove
docker compose down
```

The backend will be available at http://localhost:8000 and the frontend at http://localhost:3000.

## Environment Variables
- `MONGO_URI`: Connection string for MongoDB database.
- `NVIDIA_API_KEY`: API key for LlamaGuard endpoint to evaluate prompt safety.
- `GROQ_API_KEY`: API key for model inference (generating responses to safe prompts).
- `ALLOWED_ORIGINS`: CORS allowed origins (e.g., http://localhost:3000, your Vercel URL).
- `NEXT_PUBLIC_API_URL`: (Frontend) The base URL for the backend API (e.g., http://localhost:8000).

## API Endpoints
- `GET /`: Health check endpoint.
- `POST /analyze`: Evaluates a prompt, logs the interaction, and returns risk analysis and the generated response (if safe).
- `GET /logs`: Retrieves paginated security logs for the dashboard.

## Deployment Links
- **Frontend**: [Link Placeholder - Update with Vercel URL]
- **Backend**: [Link Placeholder - Update with Render URL]

## Screenshots
[Screenshot Placeholder - Add Dashboard View]
[Screenshot Placeholder - Add Chat Interface View]

## Future Scope
- **Advanced Behavioral Analytics**: Implement ML models to detect subtle, distributed attacks over time.
- **Automated Incident Response**: Auto-ban IPs or accounts after severe violations.
- **Customizable Security Policies**: Allow admins to configure strictness levels via the dashboard.
- **Multi-Model Support**: Extend evaluation beyond LlamaGuard to an ensemble of security models.
