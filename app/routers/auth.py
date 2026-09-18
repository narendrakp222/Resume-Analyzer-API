from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_in: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email, username, and password.
    """
    return await AuthService.register_user(db, user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="User login and JWT authentication"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with username/email and password to receive a JWT access token.
    """
    return await AuthService.authenticate_user(db, credentials)
