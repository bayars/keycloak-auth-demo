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
