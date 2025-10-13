#!/bin/bash

# Keycloak Realm Import Script
# This script provides instructions for importing the exported realm

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
    echo "Usage: $0 <keycloak-admin-url>"
    echo ""
    echo "Example:"
    echo "  $0 https://your-domain.com/auth/admin/master/console/"
    echo ""
    echo "This script will guide you through the manual import process."
}

# Manual import instructions
manual_import_instructions() {
    local admin_url="$1"
    
    echo "=========================================="
    echo "  Keycloak Realm Import Instructions"
    echo "=========================================="
    echo ""
    
    print_status "Manual Import Process:"
    echo ""
    echo "1. Access Keycloak Admin Console:"
    echo "   $admin_url"
    echo ""
    echo "2. Login with admin credentials"
    echo ""
    echo "3. Import Realm:"
    echo "   - Click 'Create Realm' or 'Import'"
    echo "   - Select 'myrealm.json' file"
    echo "   - Click 'Create' or 'Import'"
    echo ""
    echo "4. Verify Configuration:"
    echo "   - Check realm settings"
    echo "   - Verify users are created"
    echo "   - Check roles are assigned"
    echo "   - Verify clients are configured"
    echo ""
    echo "5. Update Client Configuration:"
    echo "   - Go to Clients → myapp"
    echo "   - Update Redirect URIs for your domain"
    echo "   - Update Web Origins for your domain"
    echo ""
    echo "6. Test Authentication:"
    echo "   - Try logging in with admin/admin"
    echo "   - Verify password change flow works"
    echo ""
    
    print_success "Import instructions provided"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        print_error "Keycloak admin URL is required"
        print_usage
        exit 1
    fi
    
    local admin_url="$1"
    manual_import_instructions "$admin_url"
}

# Run main function
main "$@"
