from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict

from .models import UserInfo, ErrorResponse
from .auth import get_current_user, require_admin, require_role
from .config import settings

app = FastAPI(
    title=settings.app_name,
    description="API with JWT authentication (validated by HAProxy)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/user/me", response_model=UserInfo)
async def get_user_info(current_user: Dict = Depends(get_current_user)):
    """
    Get current user information from HAProxy headers
    """
    # Extract roles from realm_access field
    realm_access = current_user.get("realm_access", {})
    roles = realm_access.get("roles", [])
    
    return UserInfo(
        username=current_user.get("preferred_username", ""),
        email=current_user.get("email"),
        roles=roles,
        first_name=current_user.get("given_name"),
        last_name=current_user.get("family_name")
    )

@app.get("/api/dashboard")
async def dashboard(current_user: Dict = Depends(get_current_user)):
    """
    Dashboard endpoint - requires authentication
    """
    return {
        "message": f"Welcome to the dashboard, {current_user.get('preferred_username')}!",
        "user": current_user.get("preferred_username"),
        "roles": current_user.get("realm_access", {}).get("roles", []),
        "issuer": current_user.get("iss"),
        "email": current_user.get("email")
    }

@app.get("/api/admin")
async def admin_endpoint(current_user: Dict = Depends(require_admin)):
    """
    Admin-only endpoint
    """
    return {
        "message": "Admin access granted",
        "user": current_user.get("preferred_username"),
        "roles": current_user.get("realm_access", {}).get("roles", [])
    }

# Packages endpoints
@app.get("/api/packages")
async def get_packages(current_user: Dict = Depends(require_role("view_dashboard", "packages_viewer"))):
    """
    Get packages - requires view_dashboard or packages_viewer role
    """
    return {
        "message": "Packages retrieved successfully",
        "user": current_user.get("preferred_username"),
        "packages": []  # Add your packages logic here
    }

@app.post("/api/packages")
async def create_package(current_user: Dict = Depends(require_role("packages_editor", "packages_admin"))):
    """
    Create package - requires packages_editor or packages_admin role
    """
    return {
        "message": "Package created successfully",
        "user": current_user.get("preferred_username")
    }

# VPN endpoints
@app.get("/api/vpn")
async def get_vpn(current_user: Dict = Depends(require_role("vpn_user", "vpn_viewer"))):
    """
    Get VPN information - requires vpn_user or vpn_viewer role
    """
    return {
        "message": "VPN information retrieved successfully",
        "user": current_user.get("preferred_username"),
        "vpn": {}  # Add your VPN logic here
    }

@app.post("/api/vpn")
async def create_vpn_config(current_user: Dict = Depends(require_role("vpn_user", "vpn_admin"))):
    """
    Create VPN configuration - requires vpn_user or vpn_admin role
    """
    return {
        "message": "VPN configuration created successfully",
        "user": current_user.get("preferred_username")
    }

# Console endpoints
@app.get("/api/console")
async def get_console(current_user: Dict = Depends(require_role("console_accesser", "console_viewer"))):
    """
    Get console access - requires console_accesser or console_viewer role
    """
    return {
        "message": "Console access granted",
        "user": current_user.get("preferred_username"),
        "console": {}  # Add your console logic here
    }

@app.post("/api/console")
async def execute_console_command(current_user: Dict = Depends(require_role("console_accesser", "console_admin"))):
    """
    Execute console command - requires console_accesser or console_admin role
    """
    return {
        "message": "Console command executed successfully",
        "user": current_user.get("preferred_username")
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
