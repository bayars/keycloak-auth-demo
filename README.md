# Keycloak Authentication GUI

A React-based frontend application for the Keycloak authentication system with Material-UI components.

## Features

- **Login Page**: Authenticate with Keycloak using username/password
- **Password Change Page**: Force admin users to change their default password
- **Dashboard Page**: Admin dashboard with Keycloak console access
- **Material-UI Design**: Modern, responsive UI components
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: Admin and user role management

## Pages

### 1. Login Page (`/login`)
- Clean login form with Material-UI components
- Default admin credentials display
- Error handling and loading states
- Redirects to password change or dashboard based on user state

### 2. Password Change Page (`/change-password`)
- Required for admin users with temporary passwords
- Password strength validation
- Password visibility toggles
- Success confirmation with auto-redirect

### 3. Dashboard Page (`/dashboard`)
- Welcome message with user information
- Role-based access indicators
- Keycloak console access button (admin only)
- User management section (admin only)
- System information display

## Architecture

```
Client Browser
    ↓
HAProxy (Port 443)
    ├── /auth/* → Keycloak Admin (admin role required)
    ├── /api/* → Backend API (JWT validation)
    ├── /static/* → Frontend Assets
    ├── /* → Frontend Application
    ↓
React Frontend (Port 3000)
```

## Setup Instructions

### 1. Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify services
docker-compose ps
```

### 2. Access the Application

- **Frontend**: https://lab-test2.safa.nisvcg.comp.net
- **Keycloak Console**: https://lab-test2.safa.nisvcg.comp.net/auth (admin only)
- **API Health**: https://lab-test2.safa.nisvcg.comp.net/health
- **HAProxy Stats**: http://localhost:8404/stats

### 3. Default Credentials

- **Username**: admin
- **Password**: admin

## Development

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Docker Development

```bash
# Build frontend image
docker build -t keycloak-gui ./gui

# Run with docker-compose
docker-compose up frontend
```

## API Integration

The frontend communicates with the backend API through the following endpoints:

- `POST /api/login` - User authentication
- `POST /api/change-password` - Password change
- `GET /api/user/me` - Current user info
- `GET /api/dashboard` - Dashboard data
- `GET /api/admin/users` - User management (admin only)

## Authentication Flow

1. **Login**: User enters credentials → API validates with Keycloak → Returns JWT token
2. **Password Change**: If `must_change_password` is true → Force password update
3. **Dashboard**: Display user info and admin features based on roles
4. **Keycloak Access**: Admin users can access `/auth` for Keycloak management

## Security Features

- JWT token validation
- Role-based access control
- Password strength requirements
- Secure cookie handling
- HTTPS enforcement
- CORS configuration

## Technologies Used

- **React 18** - Frontend framework
- **Material-UI 5** - UI component library
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **Docker** - Containerization
- **HAProxy** - Load balancer and SSL termination

## File Structure

```
gui/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── contexts/
│   │   └── AuthContext.js
│   ├── pages/
│   │   ├── LoginPage.js
│   │   ├── ChangePasswordPage.js
│   │   └── DashboardPage.js
│   ├── App.js
│   └── index.js
├── Dockerfile
├── package.json
└── docker-compose.yml
```
