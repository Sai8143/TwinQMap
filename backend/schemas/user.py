from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from backend.config.constants import UserRoles
from backend.models.base import PyObjectId

class UserCreate(BaseModel):
    """
    DTO schema for registering a new user.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    role: Optional[str] = Field(default=UserRoles.VIEWER, description="Role assigned to user")


class UserResponse(BaseModel):
    """
    DTO schema returned to API clients.
    Excludes sensitive fields like hashed password.
    """
    id: PyObjectId = Field(..., alias="id")
    username: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }


class UserLogin(BaseModel):
    """
    DTO schema for user authentication.
    """
    username: str = Field(...)
    password: str = Field(...)


class TokenPayload(BaseModel):
    """
    DTO schema representing JWT payload structure.
    """
    sub: str = Field(..., description="Subject of the token (user ID)")
    role: str = Field(..., description="Role of the authenticated user")
    exp: int = Field(..., description="Expiration timestamp")


class TokenResponse(BaseModel):
    """
    DTO schema returned upon successful authentication.
    """
    access_token: str
    token_type: str = "bearer"
    role: str
