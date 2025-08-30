#!/bin/bash

# SlopScan Backend Startup Script

set -e

echo "🚀 Starting SlopScan Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "⚙️  Please edit .env file with your API keys before running the server."
    echo "   - GROQ_API_KEY: Your Groq API key (required for AI analysis)"
    echo "   - GITHUB_TOKEN: Your GitHub token (optional - improves rate limits)"
fi

# Start the development server
echo "🌟 Starting FastAPI development server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
