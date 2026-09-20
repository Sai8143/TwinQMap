from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from backend.config.settings import settings
from backend.core.exceptions import AuthenticationException, NotAuthorizedException
from backend.models.user import User
from backend.security.jwt import decode_access_token
from typing import List, Callable

# OAuth2 schema for parsing Authorization bearer headers
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency injection helper to validate the access token and extract the current user.
    Note: For skeleton verification, this extracts claims from the JWT.
    
    Raises:
        AuthenticationException: if token is invalid or expired.
    """
    if not token:
        raise AuthenticationException("Authorization token is missing.")
        
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    
    if not user_id:
        raise AuthenticationException("Invalid token claims: sub is missing.")
        
    # Return user record based on token claims. 
    # Business logic layer will connect to UserRepository to fetch full database user.
    # In skeleton mode, we reconstruct a transient User object from JWT claims.
    return User(
        _id=user_id,
        username=payload.get("username", "token_user"),
        email=payload.get("email", "token_user@twinqmap.org"),
        hashed_password="",
        role=role or "viewer",
        is_active=True
    )


class RoleChecker:
    """
    Dependency helper to enforce role-based access control (RBAC).
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise NotAuthorizedException(
                f"User role '{current_user.role}' is not authorized to access this resource. Allowed: {self.allowed_roles}"
            )
        return current_user
