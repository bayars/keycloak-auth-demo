#!/bin/bash

# Keycloak Authentication System Startup Script

echo "🚀 Starting Keycloak Authentication System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "📦 Building and starting all services..."

# Build and start all services
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:     https://lab-test2.safa.nisvcg.comp.net"
echo "   Keycloak:     https://lab-test2.safa.nisvcg.comp.net/auth (admin only)"
echo "   API Health:   https://lab-test2.safa.nisvcg.comp.net/health"
echo "   HAProxy Stats: http://localhost:8404/stats"
echo ""
echo "⚠️  IMPORTANT: HAProxy is configured to only accept requests with hostname 'lab-test2.safa.nisvcg.comp.net'"
echo "   For local testing, add this to your /etc/hosts file:"
echo "   127.0.0.1 lab-test2.safa.nisvcg.comp.net"
echo ""
echo "🔑 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📝 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
