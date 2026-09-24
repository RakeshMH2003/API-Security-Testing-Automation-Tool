from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.discovery.models import Endpoint, AuthProfile
from app.discovery.schemas import EndpointCreate, AuthProfileCreate, OpenAPIImportRequest, PostmanImportRequest, SpiderCrawlRequest
from app.discovery.parsers import parse_openapi_spec, parse_postman_collection
from app.discovery.spider import spider_crawl_target
import uuid

async def get_endpoints_by_project(db: AsyncSession, project_id: str) -> list:
    result = await db.execute(select(Endpoint).where(Endpoint.project_id == project_id).order_by(Endpoint.method, Endpoint.path))
    return result.scalars().all()

async def create_endpoint(db: AsyncSession, project_id: str, data: EndpointCreate) -> Endpoint:
    ep = Endpoint(id=str(uuid.uuid4()), project_id=project_id, **data.model_dump())
    db.add(ep)
    await db.commit()
    await db.refresh(ep)
    return ep

async def delete_endpoint(db: AsyncSession, endpoint_id: str):
    result = await db.execute(select(Endpoint).where(Endpoint.id == endpoint_id))
    ep = result.scalars().first()
    if not ep:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    await db.delete(ep)
    await db.commit()

async def import_openapi(db: AsyncSession, project_id: str, data: OpenAPIImportRequest) -> dict:
    parsed = parse_openapi_spec(data.spec_content)
    saved = []
    for ep_data in parsed:
        ep = Endpoint(id=str(uuid.uuid4()), project_id=project_id, **ep_data)
        db.add(ep)
        saved.append(ep)
    await db.commit()
    return {"message": f"Successfully imported {len(saved)} endpoints from OpenAPI spec.", "endpoints_imported": len(saved), "endpoints": saved}

async def import_postman(db: AsyncSession, project_id: str, data: PostmanImportRequest) -> dict:
    parsed = parse_postman_collection(data.collection_content)
    saved = []
    for ep_data in parsed:
        ep = Endpoint(id=str(uuid.uuid4()), project_id=project_id, **ep_data)
        db.add(ep)
        saved.append(ep)
    await db.commit()
    return {"message": f"Successfully imported {len(saved)} endpoints from Postman collection.", "endpoints_imported": len(saved), "endpoints": saved}

async def crawl_target(db: AsyncSession, project_id: str, data: SpiderCrawlRequest) -> dict:
    discovered = await spider_crawl_target(data.target_url, data.depth)
    saved = []
    for ep_data in discovered:
        ep = Endpoint(id=str(uuid.uuid4()), project_id=project_id, target_id=data.target_id, **ep_data)
        db.add(ep)
        saved.append(ep)
    await db.commit()
    return {"message": f"Spider crawl discovered {len(saved)} endpoints.", "endpoints_imported": len(saved), "endpoints": saved}

# --- Auth Profiles ---
async def get_auth_profiles(db: AsyncSession, project_id: str) -> list:
    result = await db.execute(select(AuthProfile).where(AuthProfile.project_id == project_id))
    return result.scalars().all()

async def create_auth_profile(db: AsyncSession, project_id: str, data: AuthProfileCreate) -> AuthProfile:
    profile = AuthProfile(id=str(uuid.uuid4()), project_id=project_id, **data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

async def delete_auth_profile(db: AsyncSession, profile_id: str):
    result = await db.execute(select(AuthProfile).where(AuthProfile.id == profile_id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Auth profile not found")
    await db.delete(profile)
    await db.commit()
