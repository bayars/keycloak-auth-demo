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
