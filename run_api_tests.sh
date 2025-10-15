#!/bin/bash

# API Test Runner Script
# This script runs the API tests locally

set -e

echo "🧪 Running API Tests for Lab Test2..."

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in virtual environment
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing test dependencies..."
pip install -r requirements.txt

# Add app directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔍 Running unit tests..."
python -m pytest tests/unit/ -v --tb=short

echo "🔗 Running integration tests..."
python -m pytest tests/integration/ -v --tb=short

echo "📊 Running all tests with coverage..."
python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-report=html

echo "✅ All tests completed successfully!"
echo ""
echo "📈 Coverage report generated in htmlcov/index.html"
echo "🎯 Test results summary:"
echo "   - Unit tests: ✅ Passed"
echo "   - Integration tests: ✅ Passed"
echo "   - Coverage report: ✅ Generated"
echo ""
echo "💡 To run specific tests:"
echo "   source backend/venv/bin/activate"
echo "   python -m pytest tests/unit/test_api_endpoints.py::TestLoginEndpoint::test_login_success -v"
echo "   python -m pytest tests/integration/test_keycloak_integration.py -v"
