#!/usr/bin/env bash
# start.sh
# Starts both the FastAPI backend and the Vite frontend simultaneously.

set -e

# Function to clean up background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "========================================"
echo "⚡ Starting DSA Guide Generator"
echo "========================================"

# 1. Start Backend in the background
echo "▶ Starting FastAPI Backend on http://localhost:8000..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a brief moment to let backend initialize
sleep 2

# 2. Start Frontend in the background
echo "▶ Starting Vite Frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "========================================"
echo "✅ Both servers are running!"
echo "Press Ctrl+C to stop both servers gracefully."
echo "========================================"

# Keep the script running and wait for both processes
wait $BACKEND_PID $FRONTEND_PID
