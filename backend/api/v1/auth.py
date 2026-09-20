from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from backend.services.user import UserService
from backend.core.dependencies import get_user_service, get_current_active_user
from backend.models.user import User
from backend.security.jwt import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new researcher account"
)
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Creates a new user account with designated roles (admin, researcher, viewer).
    """
    user = await user_service.register_user(user_data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT credentials"
)
async def login(
    credentials: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """
    Validates username/password and issues a secure JWT token.
    """
    return await user_service.authenticate_user(credentials)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="OAuth2 compatible token endpoint"
)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """
    Form-based standard OAuth2 login for API Console clients.
    """
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return await user_service.authenticate_user(credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh authenticated JWT token lifetime"
)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Issues a new access token for active authenticated sessions.
    """
    from backend.config.settings import settings
    token = create_access_token(
        data={"sub": current_user.id, "username": current_user.username, "role": current_user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retrieve current authenticated user information"
)
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns user details derived from the active bearer authorization token claims.
    """
    return current_user
