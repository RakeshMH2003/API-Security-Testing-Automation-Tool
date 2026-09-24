from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.core.security import get_current_user, require_role
from app.auth.models import User
from app.auth.schemas import MessageResponse
from app.projects.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    TargetCreate, TargetResponse,
    ScopeRuleCreate, ScopeRuleResponse,
    RateLimitUpdate, RateLimitResponse
)
from app.projects import service

router = APIRouter(tags=['Projects (Phase 1)'])

# --- PROJECTS ---

@router.get('/api/v1/projects', response_model=List[ProjectResponse])
@router.get('/api/projects', response_model=List[ProjectResponse])
@router.get('/projects', response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_all_projects(db)

@router.post('/api/v1/projects', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@router.post('/api/projects', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
@router.post('/projects', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst', 'developer'))
):
    return await service.create_project(db, data, str(current_user.id))

@router.get('/api/v1/projects/{project_id}', response_model=ProjectDetailResponse)
@router.get('/api/projects/{project_id}', response_model=ProjectDetailResponse)
@router.get('/projects/{project_id}', response_model=ProjectDetailResponse)
async def get_project_details(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await service.get_project_by_id(db, project_id)

@router.put('/api/v1/projects/{project_id}', response_model=ProjectResponse)
@router.put('/api/projects/{project_id}', response_model=ProjectResponse)
@router.put('/projects/{project_id}', response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst', 'developer'))
):
    return await service.update_project(db, project_id, data)

@router.delete('/api/v1/projects/{project_id}', response_model=MessageResponse)
@router.delete('/api/projects/{project_id}', response_model=MessageResponse)
@router.delete('/projects/{project_id}', response_model=MessageResponse)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin'))
):
    await service.delete_project(db, project_id)
    return MessageResponse(message="Project deleted successfully")

# --- TARGETS ---

@router.post('/api/v1/projects/{project_id}/targets', response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
@router.post('/api/projects/{project_id}/targets', response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
@router.post('/projects/{project_id}/targets', response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def add_target(
    project_id: str,
    data: TargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst', 'developer'))
):
    return await service.add_target(db, project_id, data)

@router.delete('/api/v1/targets/{target_id}', response_model=MessageResponse)
@router.delete('/api/targets/{target_id}', response_model=MessageResponse)
@router.delete('/targets/{target_id}', response_model=MessageResponse)
async def delete_target(
    target_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst'))
):
    await service.delete_target(db, target_id)
    return MessageResponse(message="Target deleted successfully")

# --- SCOPE RULES ---

@router.post('/api/v1/projects/{project_id}/scope', response_model=ScopeRuleResponse, status_code=status.HTTP_201_CREATED)
@router.post('/api/projects/{project_id}/scope', response_model=ScopeRuleResponse, status_code=status.HTTP_201_CREATED)
@router.post('/projects/{project_id}/scope', response_model=ScopeRuleResponse, status_code=status.HTTP_201_CREATED)
async def add_scope_rule(
    project_id: str,
    data: ScopeRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst', 'developer'))
):
    return await service.add_scope_rule(db, project_id, data)

@router.delete('/api/v1/scope/{rule_id}', response_model=MessageResponse)
@router.delete('/api/scope/{rule_id}', response_model=MessageResponse)
@router.delete('/scope/{rule_id}', response_model=MessageResponse)
async def delete_scope_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst'))
):
    await service.delete_scope_rule(db, rule_id)
    return MessageResponse(message="Scope rule deleted successfully")

# --- RATE LIMIT CONFIG ---

@router.put('/api/v1/projects/{project_id}/rate-limit', response_model=RateLimitResponse)
@router.put('/api/projects/{project_id}/rate-limit', response_model=RateLimitResponse)
@router.put('/projects/{project_id}/rate-limit', response_model=RateLimitResponse)
async def update_rate_limit(
    project_id: str,
    data: RateLimitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role('admin', 'analyst', 'developer'))
):
    return await service.update_rate_limit(db, project_id, data)
