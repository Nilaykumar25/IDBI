#!/bin/bash

# MSME Financial Health Score - Setup Script
# This script helps set up the development environment

set -e

echo "================================================"
echo "MSME Financial Health Score - Setup Script"
echo "================================================"
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found $PYTHON_VERSION"
else
    echo "✗ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Found Node.js $NODE_VERSION"
else
    echo "✗ Node.js not found. Please install Node.js 18+"
    exit 1
fi

echo ""
echo "================================================"
echo "Setting up Backend..."
echo "================================================"

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate || . venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠ Please edit backend/.env with your Supabase credentials"
else
    echo "✓ .env file already exists"
fi

cd ..

echo ""
echo "================================================"
echo "Setting up Frontend..."
echo "================================================"

cd frontend

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install
echo "✓ Node.js dependencies installed"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠ Please edit frontend/.env with your Supabase credentials"
else
    echo "✓ .env file already exists"
fi

cd ..

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Set up your Supabase project:"
echo "   - Go to https://app.supabase.com/"
echo "   - Create a new project"
echo "   - Enable Email/Password authentication"
echo "   - Copy your credentials from Project Settings → API"
echo ""
echo "2. Configure environment variables:"
echo "   - Edit backend/.env with your Supabase credentials"
echo "   - Edit frontend/.env with your Supabase credentials"
echo ""
echo "3. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or . venv/Scripts/activate on Windows"
echo "   python app.py"
echo ""
echo "4. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open http://localhost:3000 in your browser"
echo ""
echo "For detailed instructions, see README.md"
echo ""
