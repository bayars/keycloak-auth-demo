#!/bin/bash

# Keycloak Authentication System - Deployment Script
# This script automates the deployment of the complete system

set -e

echo "🚀 Starting Keycloak Authentication System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if domain is provided
check_domain() {
    if [ -z "$1" ]; then
        print_warning "No domain provided. Using 'localhost' as default."
        DOMAIN="localhost"
    else
        DOMAIN="$1"
        print_status "Using domain: $DOMAIN"
    fi
}

# Generate SSL certificates
generate_certificates() {
    print_status "Generating SSL certificates..."
    
    # Create certificates directory
    mkdir -p haproxy/certs
    
    # Generate self-signed certificate
    openssl req -x509 -newkey rsa:4096 \
        -keyout haproxy/certs/server.key \
        -out haproxy/certs/server.crt \
        -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    # Create combined certificate file
    cat haproxy/certs/server.crt haproxy/certs/server.key > haproxy/certs/server.pem
    
    print_success "SSL certificates generated"
}

# Update configuration files
update_config() {
    print_status "Updating configuration files..."
    
    # Update HAProxy configuration
    sed -i "s/lab-test2.safa.nisvcg.comp.net/$DOMAIN/g" haproxy/haproxy.cfg
    
    # Update docker-compose.yml
    sed -i "s/KC_HOSTNAME: lab-test2.safa.nisvcg.comp.net/KC_HOSTNAME: $DOMAIN/g" docker-compose.yml
    
    print_success "Configuration files updated"
}

# Deploy services
deploy_services() {
    print_status "Deploying services with Docker Compose..."
    
    # Stop any existing services
    docker compose down 2>/dev/null || true
    
    # Build and start services
    docker compose up -d --build
    
    print_success "Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Keycloak to be ready
    print_status "Waiting for Keycloak..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s -k "https://$DOMAIN/auth/health" > /dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Keycloak failed to start within 60 seconds"
        exit 1
    fi
    
    print_success "Keycloak is ready"
    
    # Wait for API to be ready
    print_status "Waiting for API..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if curl -s -k "https://$DOMAIN/health" > /dev/null 2>&1; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "API failed to start within 30 seconds"
        exit 1
    fi
    
    print_success "API is ready"
}

# Setup Keycloak
setup_keycloak() {
    print_status "Setting up Keycloak realm and users..."
    
    # Wait a bit more for Keycloak to be fully ready
    sleep 10
    
    # Run the Keycloak setup script
    if [ -f "setup-keycloak.sh" ]; then
        chmod +x setup-keycloak.sh
        ./setup-keycloak.sh
    else
        print_warning "setup-keycloak.sh not found. Please run it manually."
    fi
    
    print_success "Keycloak setup completed"
}

# Display access information
show_access_info() {
    print_success "Deployment completed successfully!"
    echo ""
    echo "🌐 Access Information:"
    echo "======================"
    echo "Main Application:     https://$DOMAIN"
    echo "Keycloak Admin:       https://$DOMAIN/auth/admin/master/console/"
    echo "HAProxy Stats:        https://$DOMAIN:8404/stats"
    echo ""
    echo "👤 Default Credentials:"
    echo "========================"
    echo "Keycloak Admin:       admin / admin"
    echo "Application Admin:    admin / admin"
    echo "Test User:            ben / ben"
    echo ""
    echo "📋 Next Steps:"
    echo "=============="
    echo "1. Update your /etc/hosts file:"
    echo "   echo '127.0.0.1 $DOMAIN' >> /etc/hosts"
    echo ""
    echo "2. Access the application and change default passwords"
    echo ""
    echo "3. Review the DEPLOYMENT_GUIDE.md for detailed information"
    echo ""
    print_success "Deployment script completed!"
}

# Main execution
main() {
    echo "=========================================="
    echo "  Keycloak Authentication System Deployer"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    DOMAIN=${1:-"localhost"}
    
    # Run deployment steps
    check_docker
    check_domain "$DOMAIN"
    generate_certificates
    update_config
    deploy_services
    wait_for_services
    setup_keycloak
    show_access_info
}

# Run main function
main "$@"
