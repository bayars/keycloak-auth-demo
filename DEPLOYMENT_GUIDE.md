# Keycloak Authentication System - Deployment Guide

This guide provides complete instructions for deploying the Keycloak authentication system with HAProxy, FastAPI backend, and React frontend to a new system.

## System Requirements

- Docker and Docker Compose
- SSL certificates (or self-signed certificates for testing)
- Minimum 4GB RAM
- 10GB free disk space

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd keycloak-auth-demo
   ```

2. **Run the deployment script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Access the application:**
   - Main Application: `https://your-domain.com`
   - Keycloak Admin Console: `https://your-domain.com/auth/admin/master/console/`
   - HAProxy Stats: `https://your-domain.com:8404/stats`

## Manual Deployment Steps

### 1. SSL Certificates Setup

Create SSL certificates for your domain:

```bash
# Create certificates directory
mkdir -p haproxy/certs

# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -keyout haproxy/certs/server.key -out haproxy/certs/server.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# Create combined certificate file
cat haproxy/certs/server.crt haproxy/certs/server.key > haproxy/certs/server.pem
```

### 2. Environment Configuration

Update the following files with your domain:

**haproxy/haproxy.cfg:**
```haproxy
acl acl_your-domain hdr(host) -i your-domain.com localhost
```

**docker-compose.yml:**
```yaml
environment:
  KC_HOSTNAME: your-domain.com
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Initial Keycloak Setup

1. **Access Keycloak Admin Console:**
   - URL: `https://your-domain.com/auth/admin/master/console/`
   - Username: `admin`
   - Password: `admin`

2. **Create Realm and Users:**
   ```bash
   # Run the setup script
   ./setup-keycloak.sh
   ```

## Configuration Details

### HAProxy Configuration

The HAProxy configuration provides:
- SSL termination
- JWT token validation
- Route-based access control
- Load balancing

**Key Features:**
- `/api/login` and `/api/change-password` - No authentication required
- `/api/*` - JWT authentication required
- `/auth` - Direct Keycloak access
- Static assets served from frontend

### Backend API

The FastAPI backend provides:
- Login endpoint with Keycloak integration
- Password change functionality
- User information retrieval
- Admin user management

**Endpoints:**
- `POST /api/login` - User authentication
- `POST /api/change-password` - Password change
- `GET /api/user/me` - User information
- `GET /api/admin/users` - Admin user list

### Frontend Application

React application with Material-UI providing:
- Login page with Keycloak integration
- Password change page for required actions
- Admin dashboard with user management
- Keycloak console access

## User Management

### Default Users

After running `setup-keycloak.sh`, the following users are created:

1. **Admin User:**
   - Username: `admin`
   - Password: `admin`
   - Role: `admin`
   - Required Action: `UPDATE_PASSWORD`

2. **Test User:**
   - Username: `ben`
   - Password: `ben`
   - Role: `user`
   - Required Action: `UPDATE_PASSWORD`

### Creating Additional Users

Use the Keycloak admin console or the provided scripts:

```bash
# Create a new user
./scripts/create-user.sh username password role

# Example:
./scripts/create-user.sh john secret123 admin
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Errors:**
   ```bash
   # Regenerate certificates
   ./scripts/generate-certs.sh your-domain.com
   ```

2. **Keycloak Connection Issues:**
   ```bash
   # Check Keycloak logs
   docker logs keycloak
   
   # Restart Keycloak
   docker compose restart keycloak
   ```

3. **Frontend Not Loading:**
   ```bash
   # Check frontend logs
   docker logs keycloak-gui
   
   # Rebuild frontend
   docker compose build frontend --no-cache
   ```

### Log Locations

- **HAProxy:** `docker logs haproxy`
- **Keycloak:** `docker logs keycloak`
- **Backend API:** `docker logs backend-api`
- **Frontend:** `docker logs keycloak-gui`
- **Database:** `docker logs keycloak-db`

## Security Considerations

1. **Change Default Passwords:**
   - Update Keycloak admin password
   - Change default user passwords
   - Use strong SSL certificates

2. **Network Security:**
   - Configure firewall rules
   - Use VPN for admin access
   - Enable HTTPS only

3. **Keycloak Security:**
   - Enable MFA for admin users
   - Configure password policies
   - Set up session timeouts

## Backup and Recovery

### Backup Keycloak Data

```bash
# Backup database
docker exec keycloak-db pg_dump -U keycloak keycloak > backup.sql

# Backup Keycloak configuration
./scripts/export-realm.sh
```

### Restore from Backup

```bash
# Restore database
docker exec -i keycloak-db psql -U keycloak keycloak < backup.sql

# Restore Keycloak configuration
./scripts/import-realm.sh
```

## Monitoring

### Health Checks

- **Application:** `https://your-domain.com/health`
- **HAProxy Stats:** `https://your-domain.com:8404/stats`
- **Keycloak Health:** `https://your-domain.com/auth/health`

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Monitor logs
docker compose logs -f --tail=100
```

## Advanced Configuration

### Custom Domain Setup

1. **Update DNS records** to point to your server
2. **Update SSL certificates** for your domain
3. **Modify HAProxy configuration** with your domain
4. **Update docker-compose.yml** with your domain

### Load Balancing

For production deployments, consider:
- Multiple Keycloak instances
- Database clustering
- Redis session storage
- CDN for static assets

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Check the GitHub issues
4. Contact the development team

## License

This project is licensed under the MIT License - see the LICENSE file for details.
