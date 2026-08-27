from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.core.security import get_current_user, require_role
from app.auth.models import User
from app.auth.schemas import UserResponse, UserRoleUpdate, UserStatusUpdate
from app.auth.service import get_all_users, update_user_role, update_user_status

router = APIRouter(prefix='/api/v1/users', tags=['Users (RBAC)'])

@router.get('', response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role('admin'))
):
    return await get_all_users(db)

@router.put('/{user_id}/role', response_model=UserResponse)
async def change_user_role(
    user_id: str,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role('admin'))
):
    if str(admin_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    return await update_user_role(db, user_id, data.role)

@router.put('/{user_id}/status', response_model=UserResponse)
async def change_user_status(
    user_id: str,
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_role('admin'))
):
    if str(admin_user.id) == user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own status")
    return await update_user_status(db, user_id, data.is_active)
