from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ScanJob(Base):
    __tablename__ = 'scan_jobs'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(String(36), ForeignKey('targets.id', ondelete='SET NULL'), nullable=True)
    auth_profile_id = Column(String(36), ForeignKey('auth_profiles.id', ondelete='SET NULL'), nullable=True)
    scan_type = Column(String(50), default='full') # full, quick, owasp_top10, fuzzing
    status = Column(String(50), default='queued') # queued, running, completed, failed
    progress = Column(Integer, default=0) # 0 to 100
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    findings = relationship("VulnerabilityFinding", back_populates="scan_job", cascade="all, delete-orphan")

class VulnerabilityFinding(Base):
    __tablename__ = 'vulnerability_findings'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey('scan_jobs.id', ondelete='CASCADE'), nullable=False)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    endpoint_path = Column(String(512), nullable=False)
    http_method = Column(String(10), nullable=False, default='GET')
    owasp_category = Column(String(50), nullable=False) # e.g. API1:2023, API2:2023, API8:2023
    title = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False, default='Medium') # Critical, High, Medium, Low
    description = Column(Text, nullable=False)
    remediation = Column(Text, nullable=True)
    curl_poc = Column(Text, nullable=True)
    request_dump = Column(Text, nullable=True)
    response_dump = Column(Text, nullable=True)
    is_false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    scan_job = relationship("ScanJob", back_populates="findings")
