#!/bin/bash
set -e

echo "🚀 Voice Agent 2026 - Ubuntu Setup"
echo "===================================="

# Update
echo "📦 Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Dependencies
echo "📦 Installing system packages..."
sudo apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    git ffmpeg portaudio19-dev libportaudio2 \
    pulseaudio alsa-utils

# Python environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python deps
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# PyAudio fix for Ubuntu
echo "📦 Fixing PyAudio for Ubuntu..."
sudo apt-get install -y python3-pyaudio || \
    (pip install --upgrade setuptools && pip install pyaudio)

# Setup .env
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Edit .env with your API keys:"
    echo "    nano .env"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env: nano .env"
echo "2. Run: python3 voice_agent.py"
echo ""
