# Keycloak Authentication System - Complete Documentation

## 🎯 System Overview

This system provides a complete Keycloak authentication solution with:
- **React Frontend** with Material-UI components
- **FastAPI Backend** with JWT authentication
- **HAProxy Load Balancer** with SSL termination
- **Keycloak Authentication Server**
- **PostgreSQL Database**

## 🚀 Quick Start

### 1. Start the System
```bash
cd /root/gui
./start.sh
```

### 2. Access the Application
- **Frontend**: `https://lab-test2.safa.nisvcg.comp.net`
- **Keycloak Console**: `https://lab-test2.safa.nisvcg.comp.net/admin`
- **API Health**: `https://lab-test2.safa.nisvcg.comp.net/health`

### 3. Default Credentials
- **App Login**: `admin` / `admin` (forces password change)
- **Keycloak Console**: `admin` / `admin` (master realm)

## 🔧 Keycloak Management Commands (kc.sh)

### Prerequisites
```bash
# Access the Keycloak container
docker exec -it keycloak /bin/bash

# Configure admin CLI credentials
/opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin
```

### Realm Management
```bash
# Create a new realm
/opt/keycloak/bin/kcadm.sh create realms -s realm=myrealm -s enabled=true

# List all realms
/opt/keycloak/bin/kcadm.sh get realms

# Get realm details
/opt/keycloak/bin/kcadm.sh get realms/myrealm

# Update realm settings
/opt/keycloak/bin/kcadm.sh update realms/myrealm -s enabled=true
```

### Client Management
```bash
# Create a client
/opt/keycloak/bin/kcadm.sh create clients -r myrealm -s clientId=myapp -s enabled=true -s publicClient=true

# List clients
/opt/keycloak/bin/kcadm.sh get clients -r myrealm

# Get client details
/opt/keycloak/bin/kcadm.sh get clients/{client-id} -r myrealm

# Update client settings
/opt/keycloak/bin/kcadm.sh update clients/{client-id} -r myrealm -s enabled=true
```

### User Management
```bash
# Create a user
/opt/keycloak/bin/kcadm.sh create users -r myrealm -s username=testuser -s enabled=true -s email=test@example.com

# List users
/opt/keycloak/bin/kcadm.sh get users -r myrealm

# Get user details
/opt/keycloak/bin/kcadm.sh get users/{user-id} -r myrealm

# Set user password
/opt/keycloak/bin/kcadm.sh set-password -r myrealm --username testuser --new-password newpassword

# Update user
/opt/keycloak/bin/kcadm.sh update users/{user-id} -r myrealm -s enabled=true
```

### Role Management
```bash
# Create a role
/opt/keycloak/bin/kcadm.sh create roles -r myrealm -s name=admin

# List roles
/opt/keycloak/bin/kcadm.sh get roles -r myrealm

# Assign role to user
/opt/keycloak/bin/kcadm.sh add-roles -r myrealm --uusername testuser --rolename admin

# Remove role from user
/opt/keycloak/bin/kcadm.sh remove-roles -r myrealm --uusername testuser --rolename admin
```

### Client Scope and Mappers
```bash
# Create client scope
/opt/keycloak/bin/kcadm.sh create client-scopes -r myrealm -s name=roles -s protocol=openid-connect

# Create protocol mapper
/opt/keycloak/bin/kcadm.sh create clients/{client-id}/protocol-mappers/models -r myrealm -s name=realm-roles -s protocol=openid-connect -s protocolMapper=oidc-usermodel-realm-role-mapper -s 'config.claim.name=roles' -s 'config.access.token.claim=true'

# List client scopes
/opt/keycloak/bin/kcadm.sh get client-scopes -r myrealm
```

## 🛠 System Setup Commands

### Initial Keycloak Setup (Already Done)
```bash
# Create realm
docker exec keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=myrealm -s enabled=true

# Create client
docker exec keycloak /opt/keycloak/bin/kcadm.sh create clients -r myrealm -s clientId=myapp -s enabled=true -s publicClient=true -s 'redirectUris=["https://lab-test2.safa.nisvcg.comp.net/*"]' -s 'webOrigins=["*"]' -s standardFlowEnabled=true -s directAccessGrantsEnabled=true

# Create admin user
docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r myrealm -s username=admin -s enabled=true -s email=admin@example.com -s firstName=Admin -s lastName=User

# Set admin password
docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r myrealm --username admin --new-password admin

# Create admin role
docker exec keycloak /opt/keycloak/bin/kcadm.sh create roles -r myrealm -s name=admin

# Assign admin role
docker exec keycloak /opt/keycloak/bin/kcadm.sh add-roles -r myrealm --uusername admin --rolename admin
```

## 🧪 Testing Commands

### Test API Endpoints
```bash
# Test login
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" -X POST https://localhost/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'

# Test user info (with token)
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" -H "Authorization: Bearer YOUR_TOKEN" https://localhost/api/user/me

# Test health
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/health
```

### Test Keycloak Access
```bash
# Test Keycloak admin console
curl -k -I -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/admin/
```

### Run Comprehensive Test
```bash
./comprehensive_test.sh
```

## 🔍 Troubleshooting

### Common Issues

1. **Login not forcing password change**
   - Check if `must_change_password` is `true` in API response
   - Verify frontend is handling the response correctly

2. **Keycloak access blocked**
   - Ensure HAProxy is routing `/admin` to Keycloak
   - Check if Keycloak container is running

3. **JWT token issues**
   - Verify roles are being extracted from `realm_access.roles`
   - Check if client mappers are configured correctly

### Debug Commands
```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f [service-name]

# Test API directly
curl -k -H "Host: lab-test2.safa.nisvcg.comp.net" https://localhost/health

# Check HAProxy stats
curl http://localhost:8404/stats
```

## 📁 File Structure
```
/root/gui/
├── src/                    # React frontend
├── backend/               # FastAPI backend
├── haproxy/               # Load balancer config
├── docker-compose.yml     # Multi-service orchestration
├── start.sh               # Startup script
├── test.sh                # Basic test script
├── comprehensive_test.sh   # Full system test
└── README.md              # This documentation
```

## 🌐 URLs and Endpoints

- **Frontend**: `https://lab-test2.safa.nisvcg.comp.net`
- **Keycloak Console**: `https://lab-test2.safa.nisvcg.comp.net/admin`
- **API Health**: `https://lab-test2.safa.nisvcg.comp.net/health`
- **HAProxy Stats**: `http://localhost:8404/stats`

## 🔐 Security Notes

- HAProxy is configured to only accept requests with hostname `lab-test2.safa.nisvcg.comp.net`
- For local testing, add to `/etc/hosts`: `127.0.0.1 lab-test2.safa.nisvcg.comp.net`
- Keycloak admin console requires separate authentication (master realm)
- JWT tokens are validated by HAProxy and backend API
