#!/bin/bash
# Script to start the FastAPI backend only

echo "📦 Starting FastAPI Backend..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create a .env file with your GEMINI_API_KEY"
fi

# Check and stop existing backend if running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "🛑 Stopping existing backend on port 8000..."
    kill $(lsof -ti:8000) 2>/dev/null
    sleep 2
fi

cd backend
python main.py

