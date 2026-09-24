from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ScanJobCreate(BaseModel):
    target_id: Optional[str] = None
    auth_profile_id: Optional[str] = None
    scan_type: str = Field("full", example="full") # full, quick, owasp_top10, fuzzing

class VulnerabilityFindingResponse(BaseModel):
    id: str
    scan_id: str
    project_id: str
    endpoint_path: str
    http_method: str
    owasp_category: str
    title: str
    severity: str
    description: str
    remediation: Optional[str] = None
    curl_poc: Optional[str] = None
    request_dump: Optional[str] = None
    response_dump: Optional[str] = None
    is_false_positive: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScanJobResponse(BaseModel):
    id: str
    project_id: str
    target_id: Optional[str] = None
    auth_profile_id: Optional[str] = None
    scan_type: str
    status: str
    progress: int
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ScanJobDetailResponse(ScanJobResponse):
    findings: List[VulnerabilityFindingResponse] = []
