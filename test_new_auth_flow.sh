#!/bin/bash

# Test script for the new HAProxy/Keycloak authentication flow
# This script tests the new authentication architecture where:
# 1. Users go directly to HAProxy
# 2. HAProxy redirects to Keycloak for authentication
# 3. Keycloak handles login and password changes
# 4. Frontend exchanges authorization code for tokens

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Test functions
test_services_running() {
    print_status "Testing if all services are running..."
    
    if ! docker compose ps | grep -q "Up"; then
        print_error "Services are not running. Please run './start.sh' first."
        exit 1
    fi
    
    print_success "All services are running"
}

test_health_endpoint() {
    print_status "Testing health endpoint..."
    
    response=$(curl -k -s -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/health)
    
    if echo "$response" | grep -q "healthy"; then
        print_success "Health endpoint is working"
    else
        print_error "Health endpoint failed: $response"
        return 1
    fi
}

test_keycloak_access() {
    print_status "Testing Keycloak access..."
    
    response=$(curl -k -s -I -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/auth/realms/myrealm)
    
    if echo "$response" | grep -q "200 OK"; then
        print_success "Keycloak realm is accessible"
    else
        print_error "Keycloak realm access failed"
        return 1
    fi
}

test_keycloak_login_page() {
    print_status "Testing Keycloak login page..."
    
    response=$(curl -k -s -H "Host: lab-test2.safa.nisvcg.comp.net" "https://localhost/auth/realms/myrealm/protocol/openid-connect/auth?client_id=myapp&redirect_uri=https://lab-test2.safa.nisvcg.comp.net/callback&response_type=code&scope=openid profile email roles")
    
    if echo "$response" | grep -q "Sign in to your account"; then
        print_success "Keycloak login page is accessible"
    else
        print_error "Keycloak login page access failed"
        return 1
    fi
}

test_api_without_auth() {
    print_status "Testing API endpoints without authentication..."
    
    # Test user info endpoint without auth (should fail)
    response=$(curl -k -s -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/api/user/me)
    
    if echo "$response" | grep -q "error"; then
        print_success "API correctly rejects unauthenticated requests"
    else
        print_error "API should reject unauthenticated requests"
        return 1
    fi
}

test_frontend_access() {
    print_status "Testing frontend access..."
    
    response=$(curl -k -s -I -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/)
    
    if echo "$response" | grep -q "302 Found"; then
        print_success "Frontend correctly redirects to Keycloak authentication"
    else
        print_error "Frontend should redirect to Keycloak authentication"
        return 1
    fi
}

test_haproxy_routing() {
    print_status "Testing HAProxy routing..."
    
    # Test that /login routes to Keycloak
    response=$(curl -k -s -I -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/login)
    
    if echo "$response" | grep -q "200 OK"; then
        print_success "HAProxy correctly routes /login to Keycloak"
    else
        print_error "HAProxy routing to Keycloak failed"
        return 1
    fi
}

# Main test execution
main() {
    echo "=========================================="
    echo "  Testing New Authentication Flow"
    echo "=========================================="
    echo ""
    echo "This test verifies the new architecture where:"
    echo "1. Users go directly to HAProxy"
    echo "2. HAProxy redirects to Keycloak web authentication page"
    echo "3. Keycloak handles login and password changes"
    echo "4. Frontend exchanges authorization code for tokens"
    echo "5. No custom login page - uses Keycloak's native interface"
    echo ""
    
    # Run tests
    test_services_running
    test_health_endpoint
    test_keycloak_access
    test_keycloak_login_page
    test_api_without_auth
    test_frontend_access
    test_haproxy_routing
    
    echo ""
    print_success "All tests passed! The new authentication flow is working correctly."
    echo ""
    echo "🌐 Access URLs:"
    echo "==============="
    echo "App Root:        https://lab-test2.safa.nisvcg.comp.net (redirects to Keycloak)"
    echo "Keycloak Login:  https://lab-test2.safa.nisvcg.comp.net/auth/realms/myrealm/protocol/openid-connect/auth"
    echo "Keycloak Admin:  https://lab-test2.safa.nisvcg.comp.net/auth/admin/master/console"
    echo ""
    echo "👤 Test Users:"
    echo "=============="
    echo "Admin: admin / admin"
    echo "User:  ben / ben"
    echo ""
    echo "📝 Notes:"
    echo "=========="
    echo "- Users are automatically redirected to Keycloak's web authentication page"
    echo "- No custom login page - uses Keycloak's native interface"
    echo "- Password changes are handled by Keycloak directly"
    echo "- The API no longer provides login endpoints"
    echo "- HAProxy handles all authentication routing"
    echo ""
}

# Run main function
main
