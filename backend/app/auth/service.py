from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from datetime import datetime
from app.auth.models import User, TokenBlacklist
from app.auth.schemas import UserRegister, UserLogin, UserUpdate, PasswordChange
from app.auth.utils import hash_password, verify_password, create_access_token, create_refresh_token

async def register_user(db: AsyncSession, data: UserRegister) -> User:
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    new_user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: AsyncSession, data: UserLogin) -> dict:
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user
    }

async def get_user_by_id(db: AsyncSession, user_id: str) -> User:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def update_user_profile(db: AsyncSession, user_id: str, data: UserUpdate) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        # Check if new email is already taken
        stmt = select(User).where(User.email == data.email)
        result = await db.execute(stmt)
        if result.scalars().first() and data.email != user.email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken")
        user.email = data.email

    await db.commit()
    await db.refresh(user)
    return user

async def change_password(db: AsyncSession, user_id: str, data: PasswordChange) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

    user.password_hash = hash_password(data.new_password)
    await db.commit()
    await db.refresh(user)
    return user

async def blacklist_token(db: AsyncSession, jti: str, exp: int) -> None:
    blacklisted = TokenBlacklist(token_jti=jti, expires_at=datetime.utcfromtimestamp(exp))
    db.add(blacklisted)
    await db.commit()

async def is_token_blacklisted(db: AsyncSession, jti: str) -> bool:
    stmt = select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
    result = await db.execute(stmt)
    return result.scalars().first() is not None
