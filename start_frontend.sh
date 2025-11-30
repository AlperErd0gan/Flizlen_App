#!/bin/bash
# Script to start the Streamlit frontend only

echo "🎨 Starting Streamlit Frontend..."

# Check and stop existing frontend if running
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "🛑 Stopping existing frontend on port 8501..."
    kill $(lsof -ti:8501) 2>/dev/null
    sleep 2
fi

cd frontend
streamlit run app.py --server.port 8501

