#!/bin/bash
# Start script for Render deployment

# Get port from environment or default to 10000
PORT=${PORT:-10000}

echo "Starting server on port $PORT"

# Start the application with proper port binding
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT