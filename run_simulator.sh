#!/bin/bash
# Run the assembler0 simulator with both backend and frontend

# Function to cleanup background processes on exit
cleanup() {
    echo "Shutting down simulator..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start the backend server
echo "Starting backend server..."
cd packages/assembler0-simulator
uv run python src/assembler0_simulator/backend/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start the frontend dev server
echo "Starting frontend dev server..."
cd src/assembler0_simulator/frontend
npm run dev &
FRONTEND_PID=$!

echo "Simulator running:"
echo "  Backend:  http://localhost:1337"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait