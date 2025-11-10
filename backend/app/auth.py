from fastapi import HTTPException, Request, Header, Depends
from typing import Dict, Optional, List

async def get_current_user(
    request: Request,
    x_user: Optional[str] = Header(None),
    x_roles: Optional[str] = Header(None),
    x_groups: Optional[str] = Header(None),
    x_issuer: Optional[str] = Header(None),
    x_email: Optional[str] = Header(None),
    x_first_name: Optional[str] = Header(None),
    x_last_name: Optional[str] = Header(None),
    x_preferred_username: Optional[str] = Header(None)
) -> Dict:
    """
    Get current user information from HAProxy headers.
    HAProxy validates the JWT and extracts claims into headers.
    """
    if not x_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Parse roles from comma-separated string
    roles = []
    if x_roles:
        roles = [role.strip() for role in x_roles.split(',')]
    
    # Parse groups from comma-separated string
    groups = []
    if x_groups:
        groups = [group.strip() for group in x_groups.split(',')]
    
    return {
        "sub": x_user,
        "preferred_username": x_preferred_username or x_user,
        "email": x_email,
        "given_name": x_first_name,
        "family_name": x_last_name,
        "iss": x_issuer,
        "realm_access": {
            "roles": roles
        },
        "groups": groups
    }

async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role"""
    roles = current_user.get("realm_access", {}).get("roles", [])
    
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return current_user


def require_role(*allowed_roles: str, allowed_groups: Optional[List[str]] = None):
    """
    Dynamic role checker factory that creates a dependency function.
    
    Args:
        *allowed_roles: Variable number of role names. User must have at least one.
        allowed_groups: Optional list of group names. User must have at least one if provided.
    
    Returns:
        A dependency function that can be used with Depends()
    
    Example:
        @app.get("/api/packages")
        async def get_packages(current_user: Dict = Depends(require_role("view_dashboard", "packages_viewer"))):
            ...
    """
    async def role_checker(current_user: Dict = Depends(get_current_user)) -> Dict:
        user_roles = current_user.get("realm_access", {}).get("roles", [])
        user_groups = current_user.get("groups", [])
        
        # Check if user has any of the required roles
        has_role = any(role in user_roles for role in allowed_roles)
        
        # Check if user has any of the required groups (if specified)
        has_group = False
        if allowed_groups:
            has_group = any(group in user_groups for group in allowed_groups)
        
        # User needs either a required role OR a required group (if groups are specified)
        if not has_role and (allowed_groups is None or not has_group):
            required = list(allowed_roles)
            if allowed_groups:
                required.extend(allowed_groups)
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required: roles {list(allowed_roles)}" + 
                       (f" or groups {allowed_groups}" if allowed_groups else "")
            )
        
        return current_user
    
    return role_checker
