from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.core.security import get_current_user, require_role
from app.auth.models import User
from app.auth.schemas import MessageResponse
from app.discovery.schemas import (
    EndpointCreate, EndpointResponse, ImportSummaryResponse,
    OpenAPIImportRequest, PostmanImportRequest, SpiderCrawlRequest,
    AuthProfileCreate, AuthProfileResponse
)
from app.discovery import service

router = APIRouter(tags=["API Discovery (Phase 2)"])

# --- API Inventory (Module 09) ---
@router.get("/api/v1/projects/{project_id}/endpoints", response_model=List[EndpointResponse])
async def list_endpoints(project_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_endpoints_by_project(db, project_id)

@router.post("/api/v1/projects/{project_id}/endpoints", response_model=EndpointResponse, status_code=201)
async def add_endpoint(project_id: str, data: EndpointCreate, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst", "developer"))):
    return await service.create_endpoint(db, project_id, data)

@router.delete("/api/v1/endpoints/{endpoint_id}", response_model=MessageResponse)
async def remove_endpoint(endpoint_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst"))):
    await service.delete_endpoint(db, endpoint_id)
    return MessageResponse(message="Endpoint deleted")

# --- Module 06: OpenAPI Importer ---
@router.post("/api/v1/projects/{project_id}/import/openapi", response_model=ImportSummaryResponse, status_code=201)
async def import_openapi(project_id: str, data: OpenAPIImportRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst", "developer"))):
    return await service.import_openapi(db, project_id, data)

# --- Module 07: Postman Importer ---
@router.post("/api/v1/projects/{project_id}/import/postman", response_model=ImportSummaryResponse, status_code=201)
async def import_postman(project_id: str, data: PostmanImportRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst", "developer"))):
    return await service.import_postman(db, project_id, data)

# --- Module 08: Spider / Crawler ---
@router.post("/api/v1/projects/{project_id}/crawl", response_model=ImportSummaryResponse, status_code=201)
async def crawl_target(project_id: str, data: SpiderCrawlRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst"))):
    return await service.crawl_target(db, project_id, data)

# --- Module 10: Auth Profiles ---
@router.get("/api/v1/projects/{project_id}/auth-profiles", response_model=List[AuthProfileResponse])
async def list_auth_profiles(project_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_auth_profiles(db, project_id)

@router.post("/api/v1/projects/{project_id}/auth-profiles", response_model=AuthProfileResponse, status_code=201)
async def add_auth_profile(project_id: str, data: AuthProfileCreate, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst", "developer"))):
    return await service.create_auth_profile(db, project_id, data)

@router.delete("/api/v1/auth-profiles/{profile_id}", response_model=MessageResponse)
async def remove_auth_profile(profile_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_role("admin", "analyst"))):
    await service.delete_auth_profile(db, profile_id)
    return MessageResponse(message="Auth profile deleted")
