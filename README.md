# self-defending-gpt — local Docker run & deploy

Quick notes and commands to run the project with Docker.

Prerequisites
- Docker & Docker Compose installed
- Create a `.env` file in the repository root with the required secrets (do NOT commit it):

```env
MONGO_URI=your_mongo_uri
NVIDIA_API_KEY=your_nvidia_api_key
ALLOWED_ORIGINS=http://localhost:3000
```

Run locally with Docker Compose

```bash
# build and run in foreground
docker compose up --build

# build and run detached
docker compose up -d --build

# stop and remove
docker compose down
```

Notes
- The backend will be available at http://localhost:8000 and the frontend at http://localhost:3000
- When running via Compose the frontend will call the backend at `http://backend:8000` inside the network.
- Ensure `MONGO_URI` points to your MongoDB Atlas cluster and is URL-encoded if it contains special chars.

Deploy guidance
- You can push built images to a container registry and run them in your cloud provider, or deploy the backend to Render and the frontend to Vercel.
- Before deploying, remove any tracked `.env` files and rotate keys.
