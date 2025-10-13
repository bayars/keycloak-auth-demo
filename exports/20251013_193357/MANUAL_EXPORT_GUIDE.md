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
