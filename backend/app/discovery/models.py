from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Endpoint(Base):
    __tablename__ = 'endpoints'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(String(36), ForeignKey('targets.id', ondelete='SET NULL'), nullable=True)
    path = Column(String(512), nullable=False) # e.g. /api/v1/users/{id}
    method = Column(String(10), nullable=False, default='GET') # GET, POST, PUT, DELETE, PATCH
    summary = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, default=list) # List of query, path, header params
    request_body_schema = Column(JSON, nullable=True)
    response_schema = Column(JSON, nullable=True)
    auth_required = Column(Boolean, default=True)
    source = Column(String(50), default='openapi') # openapi, postman, crawler, manual
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuthProfile(Base):
    __tablename__ = 'auth_profiles'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False) # e.g. Staging Bearer Token
    auth_type = Column(String(50), nullable=False, default='bearer') # bearer, apikey, basic, oauth2, custom_header
    credentials = Column(JSON, nullable=False, default=dict) # e.g. {"token": "xyz"} or {"header_name": "X-API-Key", "key": "abc"}
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
