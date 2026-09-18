from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserRegister) -> UserResponse:
        # Check if email exists
        result_email = await db.execute(select(User).where(User.email == user_in.email))
        if result_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Check if username exists
        result_username = await db.execute(select(User).where(User.username == user_in.username))
        if result_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists"
            )

        new_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hash_password(user_in.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return UserResponse.model_validate(new_user)

    @staticmethod
    async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> Token:
        # Query user by username or email
        query = select(User).where(
            (User.username == credentials.username_or_email) | (User.email == credentials.username_or_email)
        )
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=user.id)
        return Token(access_token=access_token, token_type="bearer")
