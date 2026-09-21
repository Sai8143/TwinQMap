from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
import bcrypt
from passlib.context import CryptContext
from backend.config.settings import settings
from backend.core.exceptions import AuthenticationException
from backend.core.logging import general_logger

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches a hashed password.
    """
    try:
        if hashed_password.startswith("$2a$") or hashed_password.startswith("$2b$"):
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        general_logger.error(f"Error verifying password hash: {str(e)}")
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """
    Generates a secure hash from a plain text password.
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates an access token (JWT) encoding the provided user data and expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        general_logger.error(f"Error encoding JWT: {str(e)}")
        raise AuthenticationException("Failed to generate access token.")

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates an access token (JWT).
    
    Raises:
        AuthenticationException: If token is expired, invalid or tampered.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        general_logger.warning("Expired JWT signature detected.")
        raise AuthenticationException("Access token has expired.")
    except jwt.InvalidTokenError as e:
        general_logger.warning(f"Invalid JWT token: {str(e)}")
        raise AuthenticationException("Invalid access token.")
