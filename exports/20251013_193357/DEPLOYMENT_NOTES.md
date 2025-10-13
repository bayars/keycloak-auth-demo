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
