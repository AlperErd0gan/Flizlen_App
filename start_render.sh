#!/bin/bash
set -o pipefail

echo "🚀 Starting Filizlen on Render..."

# on Render, we are already in the project root
APP_DIR=$(pwd)
echo "📍 Working Directory: $APP_DIR"

# 1. Start Backend (Background)
# We don't use venv path here because Render installs libs globally in the environment
echo "📦 Starting Backend..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait a bit
sleep 5
if ! ps -p $BACKEND_PID > /dev/null; then
  echo "❌ Backend failed to start immediatley. Checking log:"
  cat backend.log
  exit 1
fi

# 2. Configure Env
export BACKEND_URL="http://localhost:8000"

# 3. Start Frontend (Foreground)
PORT="${PORT:-10000}" # Render sets $PORT, usually 10000
echo "🎨 Starting Frontend on port $PORT..."

# Use exec to replace shell with streamlit
exec streamlit run frontend/app.py \
  --server.port $PORT \
  --server.address 0.0.0.0
