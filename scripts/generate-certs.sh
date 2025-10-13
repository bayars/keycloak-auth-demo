#!/bin/bash

# SSL Certificate Generation Script
# This script generates SSL certificates for the Keycloak authentication system

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

print_usage() {
    echo "Usage: $0 <domain> [options]"
    echo ""
    echo "Options:"
    echo "  --days <number>     Certificate validity in days (default: 365)"
    echo "  --key-size <size>   RSA key size in bits (default: 4096)"
    echo "  --country <code>    Country code (default: US)"
    echo "  --state <state>     State (default: State)"
    echo "  --city <city>       City (default: City)"
    echo "  --org <org>         Organization (default: Organization)"
    echo ""
    echo "Examples:"
    echo "  $0 example.com"
    echo "  $0 example.com --days 730 --key-size 2048"
    echo "  $0 localhost --country CA --state Ontario --city Toronto"
}

# Default values
DAYS=365
KEY_SIZE=4096
COUNTRY="US"
STATE="State"
CITY="City"
ORG="Organization"

# Parse command line arguments
parse_args() {
    if [ $# -eq 0 ]; then
        print_error "Domain is required"
        print_usage
        exit 1
    fi
    
    DOMAIN="$1"
    shift
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --days)
                DAYS="$2"
                shift 2
                ;;
            --key-size)
                KEY_SIZE="$2"
                shift 2
                ;;
            --country)
                COUNTRY="$2"
                shift 2
                ;;
            --state)
                STATE="$2"
                shift 2
                ;;
            --city)
                CITY="$2"
                shift 2
                ;;
            --org)
                ORG="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
}

# Check if OpenSSL is installed
check_openssl() {
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed. Please install OpenSSL first."
        exit 1
    fi
    
    print_success "OpenSSL is installed"
}

# Create certificates directory
create_certs_dir() {
    print_status "Creating certificates directory..."
    
    mkdir -p haproxy/certs
    
    print_success "Certificates directory created"
}

# Generate private key
generate_private_key() {
    print_status "Generating private key (${KEY_SIZE} bits)..."
    
    openssl genrsa -out haproxy/certs/server.key "$KEY_SIZE"
    
    print_success "Private key generated"
}

# Generate certificate signing request
generate_csr() {
    print_status "Generating certificate signing request..."
    
    openssl req -new -key haproxy/certs/server.key -out haproxy/certs/server.csr \
        -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/CN=$DOMAIN"
    
    print_success "Certificate signing request generated"
}

# Generate self-signed certificate
generate_certificate() {
    print_status "Generating self-signed certificate (valid for $DAYS days)..."
    
    openssl x509 -req -days "$DAYS" -in haproxy/certs/server.csr \
        -signkey haproxy/certs/server.key -out haproxy/certs/server.crt
    
    print_success "Self-signed certificate generated"
}

# Create combined certificate file
create_combined_cert() {
    print_status "Creating combined certificate file..."
    
    cat haproxy/certs/server.crt haproxy/certs/server.key > haproxy/certs/server.pem
    
    print_success "Combined certificate file created"
}

# Set proper permissions
set_permissions() {
    print_status "Setting proper permissions..."
    
    chmod 600 haproxy/certs/server.key
    chmod 644 haproxy/certs/server.crt
    chmod 644 haproxy/certs/server.pem
    chmod 644 haproxy/certs/server.csr
    
    print_success "Permissions set"
}

# Display certificate information
show_cert_info() {
    print_status "Certificate information:"
    
    echo ""
    echo "📋 Certificate Details:"
    echo "======================"
    openssl x509 -in haproxy/certs/server.crt -text -noout | grep -E "(Subject:|Not Before:|Not After:|Public Key)"
    
    echo ""
    echo "🔐 Files Created:"
    echo "================"
    echo "Private Key:     haproxy/certs/server.key"
    echo "Certificate:     haproxy/certs/server.crt"
    echo "Combined:        haproxy/certs/server.pem"
    echo "CSR:             haproxy/certs/server.csr"
    
    echo ""
    echo "📅 Validity:"
    echo "============"
    echo "Valid From:      $(openssl x509 -in haproxy/certs/server.crt -noout -startdate | cut -d= -f2)"
    echo "Valid Until:     $(openssl x509 -in haproxy/certs/server.crt -noout -enddate | cut -d= -f2)"
    echo "Days Valid:      $DAYS"
}

# Clean up CSR file
cleanup() {
    print_status "Cleaning up temporary files..."
    
    rm -f haproxy/certs/server.csr
    
    print_success "Cleanup completed"
}

# Main execution
main() {
    echo "=========================================="
    echo "  SSL Certificate Generation Script"
    echo "=========================================="
    echo ""
    
    parse_args "$@"
    
    print_status "Generating SSL certificate for domain: $DOMAIN"
    print_status "Certificate validity: $DAYS days"
    print_status "Key size: $KEY_SIZE bits"
    echo ""
    
    check_openssl
    create_certs_dir
    generate_private_key
    generate_csr
    generate_certificate
    create_combined_cert
    set_permissions
    show_cert_info
    cleanup
    
    echo ""
    print_success "SSL certificate generation completed successfully!"
    echo ""
    echo "🚀 Next Steps:"
    echo "=============="
    echo "1. Update your HAProxy configuration if needed"
    echo "2. Update your docker-compose.yml with the correct domain"
    echo "3. Run: ./deploy.sh $DOMAIN"
    echo ""
    echo "⚠️  Note: This is a self-signed certificate."
    echo "   For production use, consider using a trusted CA certificate."
    echo ""
}

# Run main function
main "$@"
