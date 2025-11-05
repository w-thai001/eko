#!/bin/bash
# Quick start script for Todoist Task Hydration Server

echo "🚀 Starting Todoist Task Hydration Server..."
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env file with your API keys:"
    echo "   cp .env.example .env"
    echo "   Then edit .env with your Todoist and Anthropic API keys"
    exit 1
fi

# Check if required packages are installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: Flask not installed"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ Dependencies check passed"
echo ""
echo "📊 Dashboard will be available at: http://localhost:5000"
echo "🔌 API endpoints:"
echo "   POST /hydrate - Hydrate a task"
echo "   POST /log-completion - Log task completion"
echo "   GET /stats - Get statistics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "─────────────────────────────────────────────────────"
echo ""

# Start the server
python3 server.py
