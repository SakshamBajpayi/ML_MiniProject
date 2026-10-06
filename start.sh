#!/bin/bash
# Script to launch both the API and the React frontend

echo "=========================================================="
echo "    Starting Seismic Intelligence Platform                "
echo "=========================================================="

# Check if port 8000 is occupied and kill if necessary
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 8000..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
fi

# Check if port 5173 is occupied and kill if necessary
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 5173..."
    kill -9 $(lsof -Pi :5173 -sTCP:LISTEN -t)
fi

echo "[1/2] Starting FastAPI Backend on Port 8000..."
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "[2/2] Starting React Frontend on Port 5173..."
cd web
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo " SYSTEM ONLINE"
echo " Frontend: http://localhost:5173"
echo " Backend API: http://localhost:8000/docs"
echo " Press Ctrl+C to shut down all services."
echo "=========================================================="

# Wait for both processes
trap "kill $API_PID $FRONTEND_PID; exit" INT
wait
