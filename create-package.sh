#!/bin/bash

# Keycloak Authentication System - Package Creator
# This script creates a complete deployment package

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

# Create package directory
create_package() {
    local package_name="keycloak-auth-demo-$(date +%Y%m%d_%H%M%S)"
    local package_dir="/tmp/$package_name"
    
    print_status "Creating package: $package_name"
    
    # Create package directory
    mkdir -p "$package_dir"
    
    # Copy essential files
    cp -r backend "$package_dir/"
    cp -r src "$package_dir/"
    cp -r haproxy "$package_dir/"
    cp -r scripts "$package_dir/"
    cp -r public "$package_dir/"
    
    # Copy configuration files
    cp docker-compose.yml "$package_dir/"
    cp Dockerfile "$package_dir/"
    cp package.json "$package_dir/"
    cp .gitignore "$package_dir/"
    
    # Copy documentation
    cp README.md "$package_dir/"
    cp DEPLOYMENT_GUIDE.md "$package_dir/"
    cp EXPORT_SUMMARY.md "$package_dir/"
    cp KEYCLOAK_DOCUMENTATION.md "$package_dir/"
    
    # Copy scripts
    cp deploy.sh "$package_dir/"
    cp setup-keycloak.sh "$package_dir/"
    cp export-realm.sh "$package_dir/"
    
    # Make scripts executable
    chmod +x "$package_dir"/*.sh
    chmod +x "$package_dir/scripts"/*.sh
    
    print_success "Package created: $package_dir"
    echo "$package_dir"
}

# Create archive
create_archive() {
    local package_dir="$1"
    local archive_name="$(basename "$package_dir").tar.gz"
    local archive_path="/tmp/$archive_name"
    
    print_status "Creating archive: $archive_name"
    
    # Create tar.gz archive
    tar -czf "$archive_path" -C "$(dirname "$package_dir")" "$(basename "$package_dir")"
    
    print_success "Archive created: $archive_path"
    echo "$archive_path"
}

# Create deployment instructions
create_deployment_instructions() {
    local package_dir="$1"
    
    # Ensure directory exists
    mkdir -p "$package_dir"
    
    cat > "$package_dir/DEPLOYMENT_INSTRUCTIONS.md" << 'EOF'
# Keycloak Authentication System - Deployment Instructions

## 🚀 Quick Start

1. **Extract the package:**
   ```bash
   tar -xzf keycloak-auth-demo-YYYYMMDD_HHMMSS.tar.gz
   cd keycloak-auth-demo-YYYYMMDD_HHMMSS
   ```

2. **Deploy with your domain:**
   ```bash
   ./deploy.sh your-domain.com
   ```

3. **Access the application:**
   - Main Application: `https://your-domain.com`
   - Keycloak Admin: `https://your-domain.com/auth/admin/master/console/`

## 📋 What's Included

- Complete Keycloak authentication system
- HAProxy with SSL termination and JWT validation
- FastAPI backend with Keycloak integration
- React frontend with Material-UI
- PostgreSQL database
- Management scripts and documentation

## 👤 Default Users

- **Admin**: `admin` / `admin` (role: admin)
- **Test User**: `ben` / `ben` (role: user)

## 🔧 Management

- **User Management**: `./scripts/user-management.sh`
- **SSL Certificates**: `./scripts/generate-certs.sh`
- **Realm Export**: `./export-realm.sh`

## 📚 Documentation

- **Quick Start**: README.md
- **Complete Guide**: DEPLOYMENT_GUIDE.md
- **System Overview**: EXPORT_SUMMARY.md

## 🔒 Security

- Change default passwords immediately
- Use trusted SSL certificates for production
- Configure firewall rules appropriately

## 📞 Support

For issues, check the documentation or contact the development team.
EOF
    
    print_success "Deployment instructions created"
}

# Display package information
show_package_info() {
    local package_dir="$1"
    local archive_path="$2"
    
    echo ""
    print_success "Package creation completed successfully!"
    echo ""
    echo "📦 Package Information:"
    echo "======================"
    echo "Package Directory: $package_dir"
    echo "Archive File:      $archive_path"
    echo "Package Size:       $(du -h "$archive_path" | cut -f1)"
    echo ""
    echo "📋 Package Contents:"
    echo "==================="
    ls -la "$package_dir"
    echo ""
    echo "🚀 Deployment Instructions:"
    echo "==========================="
    echo "1. Copy the archive to your target system"
    echo "2. Extract: tar -xzf $(basename "$archive_path")"
    echo "3. Deploy: ./deploy.sh your-domain.com"
    echo ""
    echo "📚 Documentation:"
    echo "================="
    echo "- README.md: Quick start guide"
    echo "- DEPLOYMENT_GUIDE.md: Complete deployment guide"
    echo "- EXPORT_SUMMARY.md: System overview and configuration"
    echo "- DEPLOYMENT_INSTRUCTIONS.md: Package-specific instructions"
    echo ""
}

# Main execution
main() {
    echo "=========================================="
    echo "  Keycloak Authentication System Packager"
    echo "=========================================="
    echo ""
    
    # Create package
    package_dir=$(create_package)
    
    # Create deployment instructions
    create_deployment_instructions "$package_dir"
    
    # Create archive
    archive_path=$(create_archive "$package_dir")
    
    # Show package information
    show_package_info "$package_dir" "$archive_path"
    
    print_success "Package creation completed!"
    echo ""
    echo "🎯 Next Steps:"
    echo "=============="
    echo "1. Copy $archive_path to your target system"
    echo "2. Extract and deploy using the instructions"
    echo "3. Update the domain configuration"
    echo "4. Access the application"
    echo ""
}

# Run main function
main
