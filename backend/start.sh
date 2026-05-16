#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Run migrations or any other startup scripts here

# Start the Uvicorn server
PORT=${PORT:-8000}
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
