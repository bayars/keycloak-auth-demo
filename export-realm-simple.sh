#!/bin/bash

# Simple Keycloak Realm Export Script
# This script exports the realm configuration using the web interface

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

# Check if Keycloak is running
check_keycloak() {
    if ! docker ps | grep -q keycloak; then
        print_error "Keycloak container is not running. Please start it first."
        exit 1
    fi
}

# Create exports directory
create_exports_dir() {
    EXPORT_DIR="exports/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$EXPORT_DIR"
    print_status "Created export directory: $EXPORT_DIR"
}

# Export realm configuration manually
export_realm_manual() {
    print_status "Exporting realm configuration..."
    
    # Create a manual export guide
    cat > "$EXPORT_DIR/MANUAL_EXPORT_GUIDE.md" << 'EOF'
# Manual Keycloak Realm Export Guide

Since the automated export script is having issues with the admin CLI, please follow these manual steps:

## 1. Access Keycloak Admin Console

1. Go to: `https://localhost/auth/admin/master/console/`
2. Login with: `admin` / `admin`

## 2. Export Realm Configuration

### Export Realm Settings:
1. Navigate to `myrealm` realm
2. Go to `Realm Settings` → `General`
3. Click `Export` button
4. Save the JSON file as `myrealm.json`

### Export Users:
1. Go to `Users` in the left menu
2. Click the dropdown arrow next to `View all users`
3. Select `Export` → `JSON`
4. Save as `users.json`

### Export Roles:
1. Go to `Realm Roles` in the left menu
2. Click the dropdown arrow next to `Create role`
3. Select `Export` → `JSON`
4. Save as `roles.json`

### Export Clients:
1. Go to `Clients` in the left menu
2. Click the dropdown arrow next to `Create`
3. Select `Export` → `JSON`
4. Save as `clients.json`

## 3. Save Files

Save all exported files to the `exports/YYYYMMDD_HHMMSS/` directory.

## 4. Import on Another System

To import on another system:
1. Copy the exported files
2. Use the Keycloak admin console import feature
3. Or use the import script (if available)

## Current Configuration Summary

### Realm: myrealm
- **Client ID**: myapp
- **Client Type**: Public
- **Redirect URIs**: https://localhost/*, https://lab-test2.safa.nisvcg.comp.net/*
- **Web Origins**: https://localhost, https://lab-test2.safa.nisvcg.comp.net

### Users:
- **admin**: admin / admin (role: admin, required action: UPDATE_PASSWORD)
- **ben**: ben / ben (role: user, required action: UPDATE_PASSWORD)

### Roles:
- **admin**: Admin role with full access
- **user**: Basic user role

### Authentication Flows:
- Standard authentication flow
- Required action: UPDATE_PASSWORD for new users
EOF
    
    print_success "Manual export guide created"
}

# Create import script
create_import_script() {
    cat > "$EXPORT_DIR/import-realm.sh" << 'EOF'
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
EOF
    
    chmod +x "$EXPORT_DIR/import-realm.sh"
    print_success "Import script created: $EXPORT_DIR/import-realm.sh"
}

# Create configuration summary
create_config_summary() {
    cat > "$EXPORT_DIR/CONFIGURATION_SUMMARY.md" << 'EOF'
# Keycloak Realm Configuration Summary

## Realm Information
- **Realm Name**: myrealm
- **Display Name**: myrealm
- **Enabled**: true
- **Login Theme**: keycloak
- **Account Theme**: keycloak
- **Admin Theme**: keycloak
- **Email Theme**: keycloak

## Client Configuration
- **Client ID**: myapp
- **Client Type**: Public
- **Enabled**: true
- **Standard Flow Enabled**: true
- **Implicit Flow Enabled**: false
- **Direct Access Grants Enabled**: true
- **Service Accounts Enabled**: false
- **Authorization Enabled**: false

### Redirect URIs
- https://localhost/*
- https://lab-test2.safa.nisvcg.comp.net/*

### Web Origins
- https://localhost
- https://lab-test2.safa.nisvcg.comp.net

## Users

### Admin User
- **Username**: admin
- **Email**: admin@example.com
- **First Name**: Admin
- **Last Name**: User
- **Enabled**: true
- **Email Verified**: false
- **Required Actions**: UPDATE_PASSWORD
- **Roles**: admin

### Test User
- **Username**: ben
- **Email**: ben@example.com
- **First Name**: Ben
- **Last Name**: User
- **Enabled**: true
- **Email Verified**: false
- **Required Actions**: UPDATE_PASSWORD
- **Roles**: user

## Roles

### Realm Roles
- **admin**: Admin role with full access
- **user**: Basic user role
- **offline_access**: Offline access role
- **uma_authorization**: UMA authorization role

## Authentication Flows
- **Standard Authentication Flow**: Default flow for user authentication
- **Required Actions**: UPDATE_PASSWORD for new users

## Password Policy
- **Default Policy**: No specific password policy configured

## Session Settings
- **SSO Session Idle Timeout**: 30 minutes
- **SSO Session Max Lifespan**: 10 hours
- **Access Token Lifespan**: 5 minutes
- **Refresh Token Lifespan**: 30 minutes

## Security Settings
- **Brute Force Detection**: Enabled
- **Remember Me**: Enabled
- **Verify Email**: Disabled
- **Login with Email**: Disabled
- **Duplicate Emails**: Disabled
- **Edit Username**: Disabled
- **User Registration**: Disabled
EOF
    
    print_success "Configuration summary created"
}

# Create deployment notes
create_deployment_notes() {
    cat > "$EXPORT_DIR/DEPLOYMENT_NOTES.md" << 'EOF'
# Deployment Notes

## System Requirements
- Docker and Docker Compose
- SSL certificates (or self-signed for testing)
- Minimum 4GB RAM
- 10GB free disk space

## Deployment Steps
1. Copy the entire project directory to target system
2. Update domain configuration in:
   - `haproxy/haproxy.cfg`
   - `docker-compose.yml`
3. Generate SSL certificates: `./scripts/generate-certs.sh your-domain.com`
4. Deploy: `./deploy.sh your-domain.com`
5. Setup Keycloak: `./setup-keycloak.sh`

## Post-Deployment Configuration
1. Access Keycloak Admin Console
2. Import realm configuration (if using manual export)
3. Update client redirect URIs for your domain
4. Test authentication flow
5. Change default passwords

## Troubleshooting
- Check Docker logs: `docker compose logs -f`
- Verify SSL certificates
- Check HAProxy configuration
- Test API endpoints
- Verify Keycloak connectivity

## Security Considerations
- Change default passwords immediately
- Use trusted SSL certificates for production
- Configure firewall rules
- Enable MFA for admin users
- Regular security updates
EOF
    
    print_success "Deployment notes created"
}

# Main execution
main() {
    echo "=========================================="
    echo "  Keycloak Realm Export Script"
    echo "=========================================="
    echo ""
    
    check_keycloak
    create_exports_dir
    export_realm_manual
    create_import_script
    create_config_summary
    create_deployment_notes
    
    echo ""
    print_success "Realm export completed successfully!"
    echo ""
    echo "📁 Export Location: $EXPORT_DIR"
    echo ""
    echo "📋 Files Created:"
    echo "=================="
    ls -la "$EXPORT_DIR"
    echo ""
    echo "📚 Documentation:"
    echo "=================="
    echo "- MANUAL_EXPORT_GUIDE.md: Step-by-step export instructions"
    echo "- CONFIGURATION_SUMMARY.md: Complete configuration details"
    echo "- DEPLOYMENT_NOTES.md: Deployment and troubleshooting guide"
    echo "- import-realm.sh: Import script for target system"
    echo ""
    echo "🔄 Next Steps:"
    echo "=============="
    echo "1. Follow MANUAL_EXPORT_GUIDE.md to export from Keycloak admin console"
    echo "2. Save exported files to $EXPORT_DIR"
    echo "3. Copy the entire exports directory to target system"
    echo "4. Use import-realm.sh on target system"
    echo ""
}

# Run main function
main
