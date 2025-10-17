from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

security = HTTPBearer()

def decode_token(token: str) -> Dict:
    """Decode JWT token without verification (HAProxy already validated)"""
    try:
        # Since HAProxy validates, we just decode without verification
        payload = jwt.get_unverified_claims(token)
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    return payload

async def require_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    """Require admin role"""
    payload = decode_token(credentials.credentials)
    # Extract roles from realm_access field
    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", [])
    
    if "admin" not in roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return payload
