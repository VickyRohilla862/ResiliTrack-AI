#!/bin/bash
# Quick setup script for ResiliTrack AI

echo "ResiliTrack AI - Setup Script"
echo "=============================="

# Backend setup
echo ""
echo "Setting up Backend..."
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (this won't work in this script context, user needs to do manually)
echo "Virtual environment created. Please activate it manually:"
echo "  Windows: venv\Scripts\activate"
echo "  macOS/Linux: source venv/bin/activate"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env file created. Please add your GEMINI_API_KEY"
fi

cd ..

# Frontend setup
echo ""
echo "Setting up Frontend..."
cd frontend

# Install npm dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Gemini API key to backend/.env"
echo "2. Run backend: cd backend && python app.py"
echo "3. Run frontend: cd frontend && npm run dev"
