# Keycloak Authentication System - Quick Start Guide

This is a complete Keycloak authentication system with HAProxy, FastAPI backend, and React frontend.

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd keycloak-auth-demo

# Deploy with your domain
./deploy.sh your-domain.com

# Or deploy with localhost for testing
./deploy.sh localhost
```

### Option 2: Manual Deployment

```bash
# 1. Generate SSL certificates
./scripts/generate-certs.sh your-domain.com

# 2. Start services
docker compose up -d

# 3. Setup Keycloak
./setup-keycloak.sh
```

## 📋 What Gets Deployed

- **HAProxy**: SSL termination, JWT validation, load balancing
- **Keycloak**: Authentication and authorization server
- **FastAPI Backend**: REST API with Keycloak integration
- **React Frontend**: Material-UI based web application
- **PostgreSQL**: Database for Keycloak

## 🌐 Access Points

After deployment, you can access:

- **Main Application**: `https://your-domain.com`
- **Keycloak Admin Console**: `https://your-domain.com/auth/admin/master/console/`
- **HAProxy Stats**: `https://your-domain.com:8404/stats`

## 👤 Default Users

The system creates these users automatically:

- **Admin User**: `admin` / `admin` (role: admin)
- **Test User**: `ben` / `ben` (role: user)

Both users have `UPDATE_PASSWORD` required action, so they'll be prompted to change their password on first login.

## 🔧 Management Scripts

### User Management
```bash
# Create a new user
./scripts/user-management.sh create john secret123 admin

# List all users
./scripts/user-management.sh list

# Reset user password
./scripts/user-management.sh reset-password admin newpassword

# Assign role to user
./scripts/user-management.sh assign-role john user
```

### Realm Export/Import
```bash
# Export current realm configuration
./export-realm.sh

# Import realm configuration (on another system)
./exports/YYYYMMDD_HHMMSS/import-realm.sh
```

### SSL Certificates
```bash
# Generate new certificates
./scripts/generate-certs.sh your-domain.com

# Generate certificates with custom settings
./scripts/generate-certs.sh your-domain.com --days 730 --key-size 2048
```

## 🔍 Troubleshooting

### Check Service Status
```bash
docker compose ps
docker compose logs -f
```

### Common Issues

1. **SSL Certificate Errors**
   ```bash
   ./scripts/generate-certs.sh your-domain.com
   ```

2. **Keycloak Not Starting**
   ```bash
   docker logs keycloak
   docker compose restart keycloak
   ```

3. **Frontend Not Loading**
   ```bash
   docker logs keycloak-gui
   docker compose build frontend --no-cache
   ```

## 📚 Documentation

- **Complete Guide**: See `DEPLOYMENT_GUIDE.md` for detailed instructions
- **API Documentation**: Available at `https://your-domain.com/docs` (after deployment)
- **Keycloak Documentation**: [Official Keycloak Docs](https://www.keycloak.org/documentation)

## 🔒 Security Notes

- Change default passwords immediately after deployment
- Use trusted SSL certificates for production
- Configure firewall rules appropriately
- Enable MFA for admin users in production

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Check the GitHub issues
4. Contact the development team

## 📄 License

This project is licensed under the MIT License.