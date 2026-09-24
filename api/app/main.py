import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables, AsyncSessionLocal
from app.auth.models import User
from app.auth.utils import hash_password
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.projects.router import router as projects_router
from app.discovery.router import router as discovery_router
from sqlalchemy.future import select

app = FastAPI(title='API Security Testing Platform', version='2.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'],
)

@app.on_event("startup")
async def startup_event():
    try:
        await create_tables()
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == 'admin@security.local'))
            if not result.scalars().first():
                session.add(User(
                    id=str(uuid.uuid4()),
                    email='admin@security.local',
                    password_hash=hash_password('Admin@1234'),
                    full_name='Platform Admin',
                    role='admin',
                    is_active=True
                ))
                await session.commit()
                print("Default admin initialized")
    except Exception as e:
        print(f"Startup DB info: {e}")

app.include_router(auth_router, prefix='/api/v1/auth')
app.include_router(auth_router, prefix='/api/auth')
app.include_router(auth_router, prefix='/auth')
app.include_router(users_router, prefix='/api/v1/users')
app.include_router(users_router, prefix='/api/users')
app.include_router(users_router, prefix='/users')
app.include_router(projects_router)
app.include_router(discovery_router)

@app.get('/')
@app.get('/api')
@app.get('/api/health')
@app.get('/api/v1/health')
async def health():
    return {'status': 'healthy', 'version': '2.0.0', 'phase': 'Phase 1+2 Active'}
