from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.repositories.user import UserRepository
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from backend.services.base import BaseService
from backend.security.jwt import verify_password, get_password_hash, create_access_token
from backend.core.exceptions import AuthenticationException, ValidationException
from backend.core.logging import general_logger

class UserService(BaseService[User, UserRepository]):
    """
    User service orchestrating business rules, password management, and JWT token issuance.
    """
    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def register_user(self, schema: UserCreate) -> User:
        """
        Registers a new user after verifying username/email uniqueness.
        """
        # Validate uniqueness
        existing_user = await self.repository.get_by_username(schema.username)
        if existing_user:
            raise ValidationException(f"Username '{schema.username}' is already registered.")

        existing_email = await self.repository.get_by_email(schema.email)
        if existing_email:
            raise ValidationException(f"Email '{schema.email}' is already registered.")

        # Hash password and create User entity
        hashed_pw = get_password_hash(schema.password)
        new_user = User(
            username=schema.username,
            email=schema.email,
            hashed_password=hashed_pw,
            role=schema.role or "viewer",
            is_active=True
        )
        return await self.repository.create(new_user)

    async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Authenticates a user and generates JWT access tokens.
        """
        user = await self.repository.get_by_username(credentials.username)
        if not user:
            general_logger.warning(f"Auth failed: Username '{credentials.username}' not found.")
            raise AuthenticationException("Invalid username or password.")

        if not user.is_active:
            general_logger.warning(f"Auth failed: User '{credentials.username}' is inactive.")
            raise AuthenticationException("User account is disabled.")

        if not verify_password(credentials.password, user.hashed_password):
            general_logger.warning(f"Auth failed: Incorrect password for user '{credentials.username}'.")
            raise AuthenticationException("Invalid username or password.")

        # Generate tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "email": user.email
        }
        token = create_access_token(token_data)
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            role=user.role
        )
