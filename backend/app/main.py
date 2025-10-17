from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict

from .models import (
    UserInfo, ErrorResponse
)
from .auth import get_current_user, require_admin

app = FastAPI(
    title="Lab Test2 API",
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

# Login endpoint removed - authentication now handled by HAProxy/Keycloak

# Change password endpoint removed - password changes now handled by Keycloak directly

@app.get("/api/user/me", response_model=UserInfo)
async def get_user_info(current_user: Dict = Depends(get_current_user)):
    """
    Get current user information
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
        "roles": current_user.get("realm_access", {}).get("roles", [])
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
