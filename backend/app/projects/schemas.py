from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List

# Target Schemas
class TargetCreate(BaseModel):
    name: str = Field(..., example="Staging API Gateway")
    base_url: str = Field(..., example="https://api.staging.example.com")
    environment: str = Field("staging", example="staging") # production, staging, development, localhost

class TargetResponse(BaseModel):
    id: str
    project_id: str
    name: str
    base_url: str
    environment: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Scope Rule Schemas
class ScopeRuleCreate(BaseModel):
    rule_type: str = Field("include", example="include") # include, exclude
    pattern: str = Field(..., example="/api/v1/.*")
    description: Optional[str] = None

class ScopeRuleResponse(BaseModel):
    id: str
    project_id: str
    rule_type: str
    pattern: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# Rate Limit Schemas
class RateLimitUpdate(BaseModel):
    max_req_per_sec: int = Field(10, ge=1, le=1000)
    burst_limit: int = Field(20, ge=1, le=2000)
    concurrent_connections: int = Field(5, ge=1, le=100)

class RateLimitResponse(BaseModel):
    id: str
    project_id: str
    max_req_per_sec: int
    burst_limit: int
    concurrent_connections: int

    class Config:
        from_attributes = True

# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., example="CyberStore API Platform")
    description: Optional[str] = Field(None, example="Main backend e-commerce microservices")
    category: str = Field("E-Commerce", example="E-Commerce")

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    targets: List[TargetResponse] = []
    scope_rules: List[ScopeRuleResponse] = []
    rate_limit: Optional[RateLimitResponse] = None
