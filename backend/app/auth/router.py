from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.schemas import (
    UserRegister, UserLogin, UserResponse, UserUpdate,
    PasswordChange, TokenResponse, MessageResponse
)
from app.auth.service import (
    register_user, authenticate_user, update_user_profile,
    change_password, blacklist_token, get_user_by_id
)
from app.auth.utils import decode_token, create_access_token
from app.database import get_db
from app.core.security import get_current_user
from app.auth.models import User

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])
security = HTTPBearer()

@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data)
    # Auto-login after registration
    auth_data = UserLogin(email=data.email, password=data.password)
    return await authenticate_user(db, auth_data)

@router.post('/login', response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await authenticate_user(db, data)

@router.post('/logout', response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    await blacklist_token(db, payload.get('jti'), payload.get('exp'))
    return MessageResponse(message='Successfully logged out')

@router.post('/refresh', response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(credentials.credentials)
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid token type')
        
    user_id = payload.get('sub')
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
        
    access_token = create_access_token(data={'sub': user_id})
    # Keep the same refresh token
    return TokenResponse(
        access_token=access_token,
        refresh_token=credentials.credentials,
        user=user
    )

@router.get('/me', response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put('/me', response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await update_user_profile(db, str(current_user.id), data)

@router.put('/password', response_model=MessageResponse)
async def update_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await change_password(db, str(current_user.id), data)
    return MessageResponse(message='Password changed successfully')
