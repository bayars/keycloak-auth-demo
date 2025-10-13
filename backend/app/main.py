from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Dict

from .config import settings
from .models import (
    LoginRequest, LoginResponse, ChangePasswordRequest,
    UserInfo, ErrorResponse
)
from .auth import get_current_user, require_admin, decode_token, get_admin_token

app = FastAPI(
    title="Lab Test2 API",
    description="API with Keycloak authentication",
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

@app.post("/api/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - authenticates with Keycloak and returns JWT tokens
    """
    try:
        async with httpx.AsyncClient() as client:
            # Request token from Keycloak
            response = await client.post(
                f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
                data={
                    "client_id": settings.client_id,
                    "grant_type": "password",
                    "username": credentials.username,
                    "password": credentials.password,
                    "scope": "openid profile email roles"
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_data.get("error_description", "Invalid credentials")
                )
            
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Decode token to extract roles
            payload = decode_token(access_token)
            # Extract roles from realm_access field
            realm_access = payload.get("realm_access", {})
            roles = realm_access.get("roles", [])
            
            # Check if password change is required
            must_change_password = False
            try:
                # For admin user, always require password change if password is still "admin"
                if credentials.username == "admin":
                    # Check if this is the first login with default password
                    # We'll set this to true for admin user to force password change
                    must_change_password = True
            except Exception as e:
                print(f"Error checking password requirement: {e}")
                # Default to false if we can't check
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=token_data.get("refresh_token", ""),
                expires_in=token_data.get("expires_in", 0),
                roles=roles,
                must_change_password=must_change_password
            )
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Keycloak service unavailable: {str(e)}"
        )

@app.post("/api/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Change password endpoint - updates user password in Keycloak
    """
    try:
        user_id = current_user.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: missing user ID"
            )
        
        # Get admin token for Keycloak API
        admin_token = await get_admin_token()
        
        # Update password via Keycloak Admin API
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users/{user_id}/reset-password",
                headers={
                    "Authorization": f"Bearer {admin_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "type": "password",
                    "value": request.new_password,
                    "temporary": False
                }
            )
            
            if response.status_code == 204:
                # Remove "Update Password" required action
                await client.put(
                    f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    },
                    json={"requiredActions": []}
                )
                
                return {"message": "Password changed successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to change password"
                )
                
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Keycloak service unavailable: {str(e)}"
        )

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
        "roles": current_user.get("roles", [])
    }

@app.get("/api/admin/users")
async def list_users(admin_user: Dict = Depends(require_admin)):
    """
    Admin endpoint - list all users
    """
    try:
        admin_token = await get_admin_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch users"
                )
                
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Keycloak service unavailable: {str(e)}"
        )

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
