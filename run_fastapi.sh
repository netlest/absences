#!/bin/bash
# Startup script for FastAPI application
# Best practice: Provide easy startup scripts for developers

echo "Starting FastAPI Absences API..."
echo "================================"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn is not installed"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Set default environment if not set
export FLASK_ENV=${FLASK_ENV:-development}

echo "Environment: $FLASK_ENV"
echo "API will be available at: http://localhost:8000"
echo "Interactive docs: http://localhost:8000/docs"
echo "Alternative docs: http://localhost:8000/redoc"
echo ""
echo "Default test tokens:"
echo "  - demo-api-key-12345"
echo "  - test-bearer-token-67890"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

# Start the server
# Get the script's directory and cd to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
