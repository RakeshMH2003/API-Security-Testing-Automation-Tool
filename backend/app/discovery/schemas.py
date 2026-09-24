from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any, Dict

# Endpoint Schemas
class EndpointCreate(BaseModel):
    path: str = Field(..., example="/api/v1/users/{id}")
    method: str = Field("GET", example="GET")
    summary: Optional[str] = Field(None, example="Get user by ID")
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = []
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    auth_required: bool = True
    source: str = Field("manual", example="openapi") # openapi, postman, crawler, manual

class EndpointResponse(BaseModel):
    id: str
    project_id: str
    target_id: Optional[str] = None
    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = []
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    auth_required: bool
    source: str
    created_at: datetime

    class Config:
        from_attributes = True

# Import & Discovery Request Schemas
class OpenAPIImportRequest(BaseModel):
    spec_content: str = Field(..., description="Raw JSON or YAML string of OpenAPI/Swagger specification")

class PostmanImportRequest(BaseModel):
    collection_content: str = Field(..., description="Raw JSON string of Postman Collection v2.1")

class SpiderCrawlRequest(BaseModel):
    target_id: Optional[str] = None
    target_url: str = Field(..., example="https://api.staging.example.com")
    depth: int = Field(2, ge=1, le=5)

class ImportSummaryResponse(BaseModel):
    message: str
    endpoints_imported: int
    endpoints: List[EndpointResponse] = []

# Auth Profile Schemas
class AuthProfileCreate(BaseModel):
    name: str = Field(..., example="Staging Bearer Token")
    auth_type: str = Field("bearer", example="bearer") # bearer, apikey, basic, oauth2, custom_header
    credentials: Dict[str, Any] = Field(..., example={"token": "eyJhbGciOi..."})
    is_active: bool = True

class AuthProfileResponse(BaseModel):
    id: str
    project_id: str
    name: str
    auth_type: str
    credentials: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
