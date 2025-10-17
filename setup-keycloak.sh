#!/bin/bash

# Keycloak Setup Script
# This script sets up the Keycloak realm, users, and roles

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

# Wait for Keycloak to be ready
wait_for_keycloak() {
    print_status "Waiting for Keycloak to be ready..."
    
    timeout=120
    while [ $timeout -gt 0 ]; do
        if docker exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin > /dev/null 2>&1; then
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        print_error "Keycloak failed to start within 120 seconds"
        exit 1
    fi
    
    print_success "Keycloak is ready"
}

# Configure Keycloak admin CLI
configure_kcadm() {
    print_status "Configuring Keycloak admin CLI..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh config credentials \
        --server http://localhost:8080 \
        --realm master \
        --user admin \
        --password admin
    
    print_success "Keycloak admin CLI configured"
}

# Create realm
create_realm() {
    print_status "Creating realm 'myrealm'..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=myrealm -s enabled=true
    
    print_success "Realm 'myrealm' created"
}

# Create client
create_client() {
    print_status "Creating client 'myapp'..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create clients -r myrealm \
        -s clientId=myapp \
        -s enabled=true \
        -s 'redirectUris=["https://localhost/*", "https://lab-test2.safa.nisvcg.comp.net/*", "https://localhost/callback", "https://lab-test2.safa.nisvcg.comp.net/callback"]' \
        -s 'webOrigins=["https://localhost", "https://lab-test2.safa.nisvcg.comp.net"]' \
        -s publicClient=true \
        -s standardFlowEnabled=true \
        -s implicitFlowEnabled=false \
        -s directAccessGrantsEnabled=false \
        -s serviceAccountsEnabled=false \
        -s authorizationEnabled=false
    
    print_success "Client 'myapp' created with authorization code flow"
}

# Create admin role
create_admin_role() {
    print_status "Creating 'admin' role..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create roles -r myrealm -s name=admin -s description='Admin role'
    
    print_success "Admin role created"
}

# Create user role
create_user_role() {
    print_status "Creating 'user' role..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create roles -r myrealm -s name=user -s description='User role'
    
    print_success "User role created"
}

# Create admin user
create_admin_user() {
    print_status "Creating admin user..."
    
    # Create user
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r myrealm -s username=admin -s enabled=true -s email=admin@example.com -s firstName=Admin -s lastName=User
    
    # Set password
    docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r myrealm --username admin --new-password admin
    
    # Get user ID
    USER_ID=$(docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r myrealm --fields id,username | grep -A1 '"username" : "admin"' | grep '"id"' | cut -d'"' -f4)
    
    # Assign admin role
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users/$USER_ID/role-mappings/realm -r myrealm -s '[{"name":"admin"}]'
    
    # Set required action for password change
    docker exec keycloak /opt/keycloak/bin/kcadm.sh update users/$USER_ID -r myrealm -s 'requiredActions=["UPDATE_PASSWORD"]'
    
    print_success "Admin user created with password 'admin'"
}

# Create test user
create_test_user() {
    print_status "Creating test user 'ben'..."
    
    # Create user
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r myrealm -s username=ben -s enabled=true -s email=ben@example.com -s firstName=Ben -s lastName=User
    
    # Set password
    docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r myrealm --username ben --new-password ben
    
    # Get user ID
    USER_ID=$(docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r myrealm --fields id,username | grep -A1 '"username" : "ben"' | grep '"id"' | cut -d'"' -f4)
    
    # Assign user role
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users/$USER_ID/role-mappings/realm -r myrealm -s '[{"name":"user"}]'
    
    # Set required action for password change
    docker exec keycloak /opt/keycloak/bin/kcadm.sh update users/$USER_ID -r myrealm -s 'requiredActions=["UPDATE_PASSWORD"]'
    
    print_success "Test user 'ben' created with password 'ben'"
}

# Export realm configuration
export_realm() {
    print_status "Exporting realm configuration..."
    
    # Create exports directory
    mkdir -p exports
    
    # Export realm
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get realms/myrealm > exports/myrealm.json
    
    # Export users
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r myrealm > exports/users.json
    
    # Export roles
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get roles -r myrealm > exports/roles.json
    
    # Export clients
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get clients -r myrealm > exports/clients.json
    
    print_success "Realm configuration exported to exports/ directory"
}

# Main execution
main() {
    echo "=========================================="
    echo "  Keycloak Setup Script"
    echo "=========================================="
    echo ""
    
    wait_for_keycloak
    configure_kcadm
    create_realm
    create_client
    create_admin_role
    create_user_role
    create_admin_user
    create_test_user
    export_realm
    
    echo ""
    print_success "Keycloak setup completed successfully!"
    echo ""
    echo "👤 Created Users:"
    echo "=================="
    echo "Admin User:    admin / admin (role: admin)"
    echo "Test User:     ben / ben (role: user)"
    echo ""
    echo "📁 Exported Files:"
    echo "=================="
    echo "Realm Config:  exports/myrealm.json"
    echo "Users:         exports/users.json"
    echo "Roles:         exports/roles.json"
    echo "Clients:       exports/clients.json"
    echo ""
    echo "🌐 Access Keycloak Admin Console:"
    echo "https://localhost/auth/admin/master/console/"
    echo ""
}

# Run main function
main
