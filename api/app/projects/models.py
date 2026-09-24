from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = 'projects'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), default='General')
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    targets = relationship("Target", back_populates="project", cascade="all, delete-orphan")
    scope_rules = relationship("ScopeRule", back_populates="project", cascade="all, delete-orphan")
    rate_limit = relationship("RateLimitConfig", back_populates="project", uselist=False, cascade="all, delete-orphan")

class Target(Base):
    __tablename__ = 'targets'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    base_url = Column(String(512), nullable=False)
    environment = Column(String(50), default='staging') # production, staging, development, localhost
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="targets")

class ScopeRule(Base):
    __tablename__ = 'scope_rules'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    rule_type = Column(String(20), nullable=False, default='include') # include, exclude
    pattern = Column(String(512), nullable=False) # e.g. /api/v1/.*
    description = Column(String(255), nullable=True)

    project = relationship("Project", back_populates="scope_rules")

class RateLimitConfig(Base):
    __tablename__ = 'rate_limit_configs'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True)
    max_req_per_sec = Column(Integer, default=10)
    burst_limit = Column(Integer, default=20)
    concurrent_connections = Column(Integer, default=5)

    project = relationship("Project", back_populates="rate_limit")
