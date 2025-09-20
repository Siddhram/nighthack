#!/bin/bash

# Resume Relevance Check System - Development Server Starter
# This script starts both backend and frontend development servers

set -e

echo "🚀 Starting Resume Relevance Check System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if setup has been run
if [[ ! -d "backend/venv" ]] || [[ ! -d "frontend/node_modules" ]]; then
    print_warning "Setup not completed. Please run ./setup.sh first"
    exit 1
fi

# Check if .env file exists
if [[ ! -f "backend/.env" ]]; then
    print_warning "Backend .env file not found. Please copy backend/.env.example to backend/.env and configure it"
    exit 1
fi

# Function to start backend
start_backend() {
    print_status "Starting Backend Server..."
    cd backend
    source venv/bin/activate
    
    print_info "Backend starting on http://localhost:8000"
    print_info "API Documentation: http://localhost:8000/docs"
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
}

# Function to start frontend
start_frontend() {
    print_status "Starting Frontend Development Server..."
    cd frontend
    
    print_info "Frontend starting on http://localhost:3000"
    
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment for frontend to start
    sleep 3
}

# Function to cleanup processes on exit
cleanup() {
    echo ""
    print_status "Shutting down servers..."
    
    if [[ -n $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on the ports
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    print_status "Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start services
start_backend
start_frontend

echo ""
print_status "Both servers are starting up..."
echo ""
echo "📝 Access Points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running
while true; do
    sleep 1
done