#!/bin/bash
set -e

echo "🚀 Starting Flizlen Monolith..."

# 1. Start Backend (FastAPI) in the background
# We bind to 0.0.0.0:8000 so it's accessible locally within the container
echo "📦 Starting Backend on port 8000..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "   Backend PID: $BACKEND_PID"
echo "   Waiting 5 seconds for backend to initialize..."
sleep 5

# 2. Configure Environment for Frontend
# Tell Streamlit to talk to the local backend
# On Render, 'localhost' works for process-to-process communication in the same instance
export BACKEND_URL="http://localhost:8000"

# 3. Start Frontend (Streamlit) in the foreground
# Streamlit listens on the $PORT provided by Render (external access), or default to 8501 locally
PORT="${PORT:-8501}"
echo "🎨 Starting Frontend on port $PORT..."
exec streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
