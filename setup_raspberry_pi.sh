#!/bin/bash

# Webcam Viewer - Raspberry Pi Setup Script
# This script prepares a Raspberry Pi 5 for running the webcam viewer

echo "=========================================="
echo "Webcam Viewer - Raspberry Pi Setup"
echo "=========================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install OpenCV dependencies
echo "📷 Installing OpenCV dependencies..."
sudo apt-get install -y libatlas-base-dev libjasper-dev libtiff5 libjasper1 libharfbuzz0b libwebp6 libtiff5 libjasper1 libharfbuzz0b libwebp6
sudo apt-get install -y libopenjp2-7 libtiff5 libjasper1 libharfbuzz0b libwebp6 libhdf5-dev libharfbuzz0b libwebp6

# Install libsrtp for some encodings
echo "📚 Installing additional libraries..."
sudo apt-get install -y libsrtp2-1

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
cd "$(dirname "$0")"
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Then install Python dependencies:"
echo "  pip install -r backend/requirements.txt"
echo ""
echo "Finally, start the application:"
echo "  cd backend && python3 app.py"
echo ""
echo "The application will be available at:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "=========================================="
