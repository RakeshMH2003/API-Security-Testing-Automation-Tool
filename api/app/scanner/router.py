from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.core.security import get_current_user
from app.scanner.schemas import (
    ScanJobCreate, ScanJobResponse, ScanJobDetailResponse, VulnerabilityFindingResponse
)
from app.scanner.service import (
    launch_scan_job, get_scan_jobs, get_scan_job_details, get_project_findings, toggle_false_positive
)

router = APIRouter(tags=["Security Scanner"])

@router.post("/api/v1/projects/{project_id}/scans", response_model=ScanJobResponse, status_code=status.HTTP_201_CREATED)
@router.post("/projects/{project_id}/scans", response_model=ScanJobResponse, status_code=status.HTTP_201_CREATED)
async def create_scan_job(
    project_id: str,
    data: ScanJobCreate = ScanJobCreate(),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await launch_scan_job(db, project_id, data)

@router.get("/api/v1/projects/{project_id}/scans", response_model=List[ScanJobResponse])
@router.get("/projects/{project_id}/scans", response_model=List[ScanJobResponse])
async def list_scan_jobs(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_scan_jobs(db, project_id)

@router.get("/api/v1/scans/{scan_id}", response_model=ScanJobDetailResponse)
@router.get("/scans/{scan_id}", response_model=ScanJobDetailResponse)
async def read_scan_job(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_scan_job_details(db, scan_id)

@router.get("/api/v1/projects/{project_id}/findings", response_model=List[VulnerabilityFindingResponse])
@router.get("/projects/{project_id}/findings", response_model=List[VulnerabilityFindingResponse])
async def list_project_findings(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await get_project_findings(db, project_id)

@router.put("/api/v1/findings/{finding_id}/false-positive", response_model=VulnerabilityFindingResponse)
@router.put("/findings/{finding_id}/false-positive", response_model=VulnerabilityFindingResponse)
async def toggle_finding_false_positive(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await toggle_false_positive(db, finding_id)
