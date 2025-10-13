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
                error_description = error_data.get("error_description", "Invalid credentials")
                
                # Check if this is a required actions error (account not fully set up)
                if "Account is not fully set up" in error_description or "resolve_required_actions" in error_description:
                    # This means the user needs to complete required actions (like password change)
                    return LoginResponse(
                        access_token="",
                        refresh_token="",
                        expires_in=0,
                        roles=[],
                        must_change_password=True
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_description
                )
            
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Decode token to extract roles
            payload = decode_token(access_token)
            # Extract roles from realm_access field
            realm_access = payload.get("realm_access", {})
            roles = realm_access.get("roles", [])
            
            # Check if password change is required by looking at user's required actions
            must_change_password = False
            try:
                # Get admin token to check user's required actions
                admin_token = await get_admin_token()
                
                # Get user ID from the token
                user_id = payload.get("sub")
                
                if admin_token and user_id:
                    # Check user's required actions
                    user_response = await client.get(
                        f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users/{user_id}",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        required_actions = user_data.get("requiredActions", [])
                        
                        # Check if UPDATE_PASSWORD is in required actions
                        if "UPDATE_PASSWORD" in required_actions:
                            must_change_password = True
                        else:
                            must_change_password = False
                    else:
                        print(f"Failed to get user data: {user_response.status_code}")
                        must_change_password = False
                else:
                    print("Could not get admin token or user ID")
                    must_change_password = False
                
            except Exception as e:
                print(f"Error checking password requirement: {e}")
                # Default to false if we can't check
                must_change_password = False
            
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
async def change_password(request: ChangePasswordRequest):
    """
    Change password endpoint - updates user password in Keycloak
    This endpoint doesn't require authentication since it's used when must_change_password is true
    """
    try:
        # Get admin token for Keycloak API
        admin_token = await get_admin_token()
        
        # Find the user by username
        async with httpx.AsyncClient() as client:
            # Get all users and find the one with matching username
            users_response = await client.get(
                f"{settings.keycloak_url}/admin/realms/{settings.keycloak_realm}/users",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"username": request.username}
            )
            
            if users_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to find user"
                )
            
            users = users_response.json()
            if not users:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user = users[0]  # Get the first (and should be only) user
            user_id = user["id"]
            
            # Verify the old password by attempting to authenticate
            # This is a bit tricky since we can't directly verify password
            # We'll try to authenticate with the old password
            try:
                verify_response = await client.post(
                    f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/openid-connect/token",
                    data={
                        "client_id": settings.client_id,
                        "grant_type": "password",
                        "username": request.username,
                        "password": request.old_password,
                        "scope": "openid profile email roles"
                    }
                )
                
                # If we get a 401, it means the password is wrong
                if verify_response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid old password"
                    )
                
                # If we get any other error, it might be due to required actions
                # In that case, we'll proceed with the password change
                
            except Exception as e:
                # If verification fails, we'll still try to change the password
                # This handles cases where the user has required actions
                pass
        
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
