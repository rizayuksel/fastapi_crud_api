from fastapi import APIRouter, Depends
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.exceptions import AppException, AuthenticationError
from app.models import User
from app.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email is already taken
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise AppException(message="Email already registered", status_code=400, code="EMAIL_TAKEN")

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    # If user doesn't exist or password is wrong...
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AuthenticationError(message="Incorrect email or password")

    # Keeping it standard with 'sub'
    payload = {"sub": str(user.id)}

    return TokenResponse(
        access_token=create_access_token(data=payload),
        refresh_token=create_refresh_token(data=payload),
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Dynamic update is cleaner than a bunch of if statements
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    await db.flush()
    await db.refresh(current_user)

    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(
            token_data.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh" or not user_id:
            raise AuthenticationError(message="Invalid refresh token")

    except JWTError:
        raise AuthenticationError(message="Invalid or expired refresh token")

    # Re-verify user still exists
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise AuthenticationError(message="Invalid refresh token")

    new_payload = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(data=new_payload),
        refresh_token=create_refresh_token(data=new_payload),
    )
