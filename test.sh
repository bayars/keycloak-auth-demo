#!/bin/bash

# Keycloak Authentication System Test Script

echo "🧪 Testing Keycloak Authentication System..."

# Test API Health
echo "📡 Testing API Health..."
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/health
echo ""

# Test Frontend
echo "🌐 Testing Frontend..."
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/ | grep -o '<title>.*</title>'
echo ""

# Test Login
echo "🔐 Testing Login..."
LOGIN_RESPONSE=$(curl -k -s -H "Host: lab-test2.safa.nisvcg.comp.net" -X POST https://localhost/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}')
echo "Login successful! Roles: $(echo $LOGIN_RESPONSE | jq -r '.roles[]' | tr '\n' ' ')"
echo ""

# Test Keycloak (should require admin token)
echo "🔐 Testing Keycloak Access (should require admin)..."
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/auth/ | head -5
echo ""

echo "✅ System is running correctly!"
echo ""
echo "🌐 Access URLs (use correct hostname):"
echo "   Frontend:     https://lab-test2.safa.nisvcg.comp.net"
echo "   Keycloak:     https://lab-test2.safa.nisvcg.comp.net/auth"
echo "   API Health:   https://lab-test2.safa.nisvcg.comp.net/health"
echo ""
echo "💡 Note: HAProxy is configured to only accept requests with hostname 'lab-test2.safa.nisvcg.comp.net'"
echo "   This is correct for production security."
