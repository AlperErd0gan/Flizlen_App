#!/bin/bash

echo "🚀 Starting Flizlen Monolith..."

set -o pipefail

APP_DIR="/home/ubuntu/flizlen"
VENV_PY="$APP_DIR/venv/bin/python"

# 1. Start Backend
echo "📦 Starting Backend on port 8000..."
$VENV_PY -m uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  > backend.log 2>&1 &

BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

sleep 5

if ! ss -tulpn | grep -q ":8000"; then
  echo "❌ Backend failed to start. Check backend.log"
  exit 1
fi

# 2. Frontend env
export BACKEND_URL="http://localhost:8000"

# 3. Start Frontend (foreground)
PORT="${PORT:-8501}"
echo "🎨 Starting Frontend on port $PORT..."

exec $VENV_PY -m streamlit run frontend/app.py \
  --server.address 0.0.0.0 \
  --server.port "$PORT"
