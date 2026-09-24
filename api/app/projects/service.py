from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.projects.models import Project, Target, ScopeRule, RateLimitConfig
from app.projects.schemas import ProjectCreate, ProjectUpdate, TargetCreate, ScopeRuleCreate, RateLimitUpdate

# --- PROJECTS ---

async def create_project(db: AsyncSession, data: ProjectCreate, owner_id: str) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        category=data.category or 'General',
        owner_id=owner_id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Initialize default rate limit config
    rate_limit = RateLimitConfig(project_id=project.id, max_req_per_sec=10, burst_limit=20, concurrent_connections=5)
    db.add(rate_limit)

    # Add default target if base URL can be assumed or leave empty
    # Add default scope rule
    default_scope = ScopeRule(project_id=project.id, rule_type="include", pattern="/.*", description="Default include all endpoints")
    db.add(default_scope)

    await db.commit()
    await db.refresh(project)
    return project

async def get_all_projects(db: AsyncSession) -> list[Project]:
    stmt = select(Project).options(
        selectinload(Project.targets),
        selectinload(Project.scope_rules),
        selectinload(Project.rate_limit)
    ).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_project_by_id(db: AsyncSession, project_id: str) -> Project:
    stmt = select(Project).options(
        selectinload(Project.targets),
        selectinload(Project.scope_rules),
        selectinload(Project.rate_limit)
    ).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

async def update_project(db: AsyncSession, project_id: str, data: ProjectUpdate) -> Project:
    project = await get_project_by_id(db, project_id)
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.category is not None:
        project.category = data.category
    await db.commit()
    await db.refresh(project)
    return project

async def delete_project(db: AsyncSession, project_id: str) -> None:
    project = await get_project_by_id(db, project_id)
    await db.delete(project)
    await db.commit()

# --- TARGETS ---

async def add_target(db: AsyncSession, project_id: str, data: TargetCreate) -> Target:
    await get_project_by_id(db, project_id) # Validate project exists
    target = Target(
        project_id=project_id,
        name=data.name,
        base_url=data.base_url.rstrip('/'),
        environment=data.environment.lower()
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target

async def delete_target(db: AsyncSession, target_id: str) -> None:
    stmt = select(Target).where(Target.id == target_id)
    result = await db.execute(stmt)
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
    await db.delete(target)
    await db.commit()

# --- SCOPE RULES ---

async def add_scope_rule(db: AsyncSession, project_id: str, data: ScopeRuleCreate) -> ScopeRule:
    await get_project_by_id(db, project_id)
    rule = ScopeRule(
        project_id=project_id,
        rule_type=data.rule_type.lower(),
        pattern=data.pattern,
        description=data.description
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

async def delete_scope_rule(db: AsyncSession, rule_id: str) -> None:
    stmt = select(ScopeRule).where(ScopeRule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalars().first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scope rule not found")
    await db.delete(rule)
    await db.commit()

# --- RATE LIMIT CONFIG ---

async def update_rate_limit(db: AsyncSession, project_id: str, data: RateLimitUpdate) -> RateLimitConfig:
    stmt = select(RateLimitConfig).where(RateLimitConfig.project_id == project_id)
    result = await db.execute(stmt)
    config = result.scalars().first()
    if not config:
        config = RateLimitConfig(
            project_id=project_id,
            max_req_per_sec=data.max_req_per_sec,
            burst_limit=data.burst_limit,
            concurrent_connections=data.concurrent_connections
        )
        db.add(config)
    else:
        config.max_req_per_sec = data.max_req_per_sec
        config.burst_limit = data.burst_limit
        config.concurrent_connections = data.concurrent_connections

    await db.commit()
    await db.refresh(config)
    return config
