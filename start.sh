#!/bin/bash
# ResiliTrack AI - Start Backend and Frontend (macOS/Linux)

echo ""
echo "========================================"
echo "ResiliTrack AI - Startup Script"
echo "========================================"
echo ""

# Start Backend
echo "Starting ResiliTrack AI on Port 5000..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

# Wait a moment
sleep 2

# Start Frontend
# echo "Starting Frontend on Port 5173..."
# cd ../frontend
# npm run dev &
# FRONTEND_PID=$!

cd ..

echo ""
echo "========================================"
echo "Services Started!"
echo "========================================"
echo ""
# echo "Frontend:  http://localhost:5173"
echo "ResiliTrack AI :   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait
