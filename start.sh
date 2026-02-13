#!/bin/bash

# Start script for OpenClawAgents

echo "🚀 Starting OpenClawAgents..."

# Check if virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python -m venv .venv
    cd ..
fi

# Activate virtual environment and start backend
echo "🔧 Starting backend server..."
cd backend
source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python main.py &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ OpenClawAgents is running!"
echo "📊 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

