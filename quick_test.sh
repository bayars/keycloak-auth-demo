#!/bin/bash

# Quick API Test Runner
# This script runs tests quickly without full setup

set -e

echo "🚀 Quick API Test Run..."

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./run_api_tests.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v --tb=short

echo "✅ Tests completed!"
