#!/bin/bash
# Script to start both backend and frontend

echo "🚀 Starting Filizlen App..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create a .env file with your GEMINI_API_KEY"
    echo "   You can copy env.example to .env: cp env.example .env"
    echo ""
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check and stop existing backend if running
if check_port 8000; then
    echo "🛑 Stopping existing backend on port 8000..."
    kill $(lsof -ti:8000) 2>/dev/null
    sleep 2
fi

# Check and stop existing frontend if running
if check_port 8501; then
    echo "🛑 Stopping existing frontend on port 8501..."
    kill $(lsof -ti:8501) 2>/dev/null
    sleep 2
fi

# Start backend
# Start backend
echo "📦 Starting FastAPI backend..."
python -m backend.main > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend started (PID: $BACKEND_PID)"
echo "   Logs: backend.log"
sleep 3

# Check if backend started successfully
if check_port 8000; then
    echo "   ✅ Backend is running on http://localhost:8000"
else
    echo "   ❌ Backend failed to start. Check backend.log for errors"
    exit 1
fi

# Start frontend
echo ""
echo "🎨 Starting Streamlit frontend..."
cd frontend
streamlit run app.py --server.port 8501 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend started (PID: $FRONTEND_PID)"
echo "   Logs: frontend.log"
sleep 3

# Check if frontend started successfully
if check_port 8501; then
    echo "   ✅ Frontend is running on http://localhost:8501"
else
    echo "   ❌ Frontend failed to start. Check frontend.log for errors"
    exit 1
fi

echo ""
echo "✨ Filizlen App is running!"
echo ""
echo "📍 Access points:"
echo "   Frontend: http://localhost:8501"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop the app, run: ./stop.sh"
echo "   Or manually kill PIDs: $BACKEND_PID and $FRONTEND_PID"
echo ""

