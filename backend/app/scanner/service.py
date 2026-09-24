from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.scanner.models import ScanJob, VulnerabilityFinding
from app.scanner.schemas import ScanJobCreate
from app.scanner.engine import analyze_endpoints_for_vulnerabilities
from app.discovery.service import get_endpoints_by_project
from app.projects.service import get_project_by_id
import uuid
from datetime import datetime

async def launch_scan_job(db: AsyncSession, project_id: str, data: ScanJobCreate) -> ScanJob:
    project = await get_project_by_id(db, project_id)
    endpoints = await get_endpoints_by_project(db, project_id)

    scan_job = ScanJob(
        id=str(uuid.uuid4()),
        project_id=project_id,
        target_id=data.target_id,
        auth_profile_id=data.auth_profile_id,
        scan_type=data.scan_type,
        status='running',
        progress=10
    )
    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)

    # Convert endpoints to dict format for rules engine
    ep_dicts = [{"path": ep.path, "method": ep.method, "auth_required": ep.auth_required, "parameters": ep.parameters or []} for ep in endpoints]
    
    # Run analysis
    raw_findings = analyze_endpoints_for_vulnerabilities(ep_dicts)

    critical = high = medium = low = 0
    saved_findings = []

    for f_data in raw_findings:
        sev = f_data["severity"]
        if sev == "Critical": critical += 1
        elif sev == "High": high += 1
        elif sev == "Medium": medium += 1
        elif sev == "Low": low += 1

        finding = VulnerabilityFinding(
            id=str(uuid.uuid4()),
            scan_id=scan_job.id,
            project_id=project_id,
            **f_data
        )
        db.add(finding)
        saved_findings.append(finding)

    scan_job.status = 'completed'
    scan_job.progress = 100
    scan_job.total_findings = len(saved_findings)
    scan_job.critical_count = critical
    scan_job.high_count = high
    scan_job.medium_count = medium
    scan_job.low_count = low
    scan_job.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(scan_job)
    return scan_job

async def get_scan_jobs(db: AsyncSession, project_id: str) -> list:
    stmt = select(ScanJob).where(ScanJob.project_id == project_id).order_by(ScanJob.started_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_scan_job_details(db: AsyncSession, scan_id: str) -> ScanJob:
    stmt = select(ScanJob).options(selectinload(ScanJob.findings)).where(ScanJob.id == scan_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job

async def get_project_findings(db: AsyncSession, project_id: str) -> list:
    stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.project_id == project_id).order_by(VulnerabilityFinding.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def toggle_false_positive(db: AsyncSession, finding_id: str) -> VulnerabilityFinding:
    stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.id == finding_id)
    result = await db.execute(stmt)
    finding = result.scalars().first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    finding.is_false_positive = not finding.is_false_positive
    await db.commit()
    await db.refresh(finding)
    return finding
