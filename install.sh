#!/usr/bin/env bash
# install.sh
# Automates the setup of both backend and frontend environments.

set -e # Exit immediately if a command exits with a non-zero status

echo "========================================"
echo "⚡ Setting up DSA Guide Generator"
echo "========================================"

# 1. Setup Backend
echo "▶ Setting up Python Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Return to root
cd ..

# 2. Setup Frontend
echo "▶ Setting up Vite Frontend..."
cd frontend
echo "Installing npm dependencies..."
npm install

echo "========================================"
echo "✅ Installation Complete!"
echo "To start the application, run: ./start.sh"
echo "========================================"
