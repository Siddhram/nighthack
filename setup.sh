#!/bin/bash

# Resume Relevance Check System - Development Setup Script
# This script sets up both backend and frontend for development

set -e  # Exit on any error

echo "🚀 Setting up Resume Relevance Check System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking system requirements..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    print_error "Python 3.9 or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi
print_status "Python $PYTHON_VERSION found"

# Check Node.js version
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js 18 or higher is required. Found: $(node --version)"
    exit 1
fi
print_status "Node.js $(node --version) found"

# Backend setup
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
if [[ ! -d "venv" ]]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
print_status "Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_warning "Please edit backend/.env and add your OpenAI API key"
fi

# Create uploads directory
mkdir -p uploads

# Initialize database (create tables)
print_status "Initializing database..."
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

cd ..

print_status "Setup completed successfully!"

echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "🔗 API Documentation will be available at: http://localhost:8000/docs"
echo ""
print_warning "Make sure to set your OpenAI API key in backend/.env before starting the services"