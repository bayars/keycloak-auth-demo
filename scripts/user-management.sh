#!/bin/bash

# Keycloak User Management Script
# This script provides utilities for managing users in Keycloak

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
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  create <username> <password> <role>  - Create a new user"
    echo "  list                                - List all users"
    echo "  delete <username>                   - Delete a user"
    echo "  reset-password <username> <password> - Reset user password"
    echo "  assign-role <username> <role>       - Assign role to user"
    echo "  remove-role <username> <role>       - Remove role from user"
    echo ""
    echo "Examples:"
    echo "  $0 create john secret123 admin"
    echo "  $0 list"
    echo "  $0 reset-password admin newpassword"
    echo "  $0 assign-role john user"
}

# Configure Keycloak admin CLI
configure_kcadm() {
    docker exec keycloak /opt/keycloak/bin/kcadm.sh config credentials \
        --server http://localhost:8080 \
        --realm master \
        --user admin \
        --password admin > /dev/null 2>&1
}

# Get user ID by username
get_user_id() {
    local username="$1"
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r myrealm --fields id,username | grep -A1 "\"username\" : \"$username\"" | grep '"id"' | cut -d'"' -f4
}

# Create user
create_user() {
    local username="$1"
    local password="$2"
    local role="$3"
    
    if [ -z "$username" ] || [ -z "$password" ] || [ -z "$role" ]; then
        print_error "Usage: create <username> <password> <role>"
        exit 1
    fi
    
    print_status "Creating user '$username' with role '$role'..."
    
    # Create user
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r myrealm \
        -s username="$username" \
        -s enabled=true \
        -s email="${username}@example.com" \
        -s firstName="$username" \
        -s lastName="User"
    
    # Set password
    docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r myrealm \
        --username "$username" \
        --new-password "$password"
    
    # Get user ID
    local user_id=$(get_user_id "$username")
    
    if [ -z "$user_id" ]; then
        print_error "Failed to get user ID for '$username'"
        exit 1
    fi
    
    # Assign role
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users/$user_id/role-mappings/realm -r myrealm \
        -s "[{\"name\":\"$role\"}]"
    
    # Set required action for password change
    docker exec keycloak /opt/keycloak/bin/kcadm.sh update users/$user_id -r myrealm \
        -s 'requiredActions=["UPDATE_PASSWORD"]'
    
    print_success "User '$username' created successfully with password '$password' and role '$role'"
}

# List users
list_users() {
    print_status "Listing all users..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh get users -r myrealm --fields id,username,email,enabled,createdTimestamp | jq -r '.[] | "\(.username) | \(.email // "N/A") | \(.enabled) | \(.createdTimestamp)"' | column -t -s '|'
    
    print_success "Users listed"
}

# Delete user
delete_user() {
    local username="$1"
    
    if [ -z "$username" ]; then
        print_error "Usage: delete <username>"
        exit 1
    fi
    
    print_status "Deleting user '$username'..."
    
    local user_id=$(get_user_id "$username")
    
    if [ -z "$user_id" ]; then
        print_error "User '$username' not found"
        exit 1
    fi
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh delete users/$user_id -r myrealm
    
    print_success "User '$username' deleted successfully"
}

# Reset password
reset_password() {
    local username="$1"
    local password="$2"
    
    if [ -z "$username" ] || [ -z "$password" ]; then
        print_error "Usage: reset-password <username> <password>"
        exit 1
    fi
    
    print_status "Resetting password for user '$username'..."
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r myrealm \
        --username "$username" \
        --new-password "$password"
    
    print_success "Password reset successfully for user '$username'"
}

# Assign role
assign_role() {
    local username="$1"
    local role="$2"
    
    if [ -z "$username" ] || [ -z "$role" ]; then
        print_error "Usage: assign-role <username> <role>"
        exit 1
    fi
    
    print_status "Assigning role '$role' to user '$username'..."
    
    local user_id=$(get_user_id "$username")
    
    if [ -z "$user_id" ]; then
        print_error "User '$username' not found"
        exit 1
    fi
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh create users/$user_id/role-mappings/realm -r myrealm \
        -s "[{\"name\":\"$role\"}]"
    
    print_success "Role '$role' assigned to user '$username'"
}

# Remove role
remove_role() {
    local username="$1"
    local role="$2"
    
    if [ -z "$username" ] || [ -z "$role" ]; then
        print_error "Usage: remove-role <username> <role>"
        exit 1
    fi
    
    print_status "Removing role '$role' from user '$username'..."
    
    local user_id=$(get_user_id "$username")
    
    if [ -z "$user_id" ]; then
        print_error "User '$username' not found"
        exit 1
    fi
    
    docker exec keycloak /opt/keycloak/bin/kcadm.sh delete users/$user_id/role-mappings/realm -r myrealm \
        -s "[{\"name\":\"$role\"}]"
    
    print_success "Role '$role' removed from user '$username'"
}

# Main execution
main() {
    if [ $# -eq 0 ]; then
        print_usage
        exit 1
    fi
    
    local command="$1"
    shift
    
    # Configure Keycloak admin CLI
    configure_kcadm
    
    case "$command" in
        "create")
            create_user "$@"
            ;;
        "list")
            list_users
            ;;
        "delete")
            delete_user "$@"
            ;;
        "reset-password")
            reset_password "$@"
            ;;
        "assign-role")
            assign_role "$@"
            ;;
        "remove-role")
            remove_role "$@"
            ;;
        *)
            print_error "Unknown command: $command"
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
