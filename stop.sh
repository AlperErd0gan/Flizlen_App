#!/bin/bash
# Script to stop both backend and frontend

echo "🛑 Stopping Flizlen App..."

# Stop backend
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   Stopping backend on port 8000..."
    kill $(lsof -ti:8000) 2>/dev/null
    sleep 1
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️  Backend is not running"
fi

# Stop frontend
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "   Stopping frontend on port 8501..."
    kill $(lsof -ti:8501) 2>/dev/null
    sleep 1
    echo "   ✅ Frontend stopped"
else
    echo "   ℹ️  Frontend is not running"
fi

echo ""
echo "✨ All services stopped"

