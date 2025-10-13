from pydantic import BaseModel
from typing import List, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    roles: List[str]
    must_change_password: bool = False

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserInfo(BaseModel):
    username: str
    email: Optional[str] = None
    roles: List[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
