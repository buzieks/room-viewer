#!/bin/bash

# Webcam Viewer - Start Script for Raspberry Pi
# Run this script to start the webcam viewer

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Webcam Viewer..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run setup_raspberry_pi.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if packages are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Python packages..."
    pip install -r backend/requirements.txt
fi

# Start the application
echo "🚀 Starting application..."
echo "Access the viewer at: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

cd backend
python3 app.py

# Deactivate virtual environment on exit
deactivate
