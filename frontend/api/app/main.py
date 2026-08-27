import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables, get_db, AsyncSessionLocal
from app.auth.models import User
from app.auth.utils import hash_password
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from sqlalchemy.future import select

app = FastAPI(
    title='API Security Testing Platform',
    version='1.0.0',
    description='Automated API Security Testing with OWASP API Top 10 coverage'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event("startup")
async def startup_event():
    try:
        await create_tables()
        # Seed default admin user if none exists
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == 'admin@security.local'))
            admin = result.scalars().first()
            if not admin:
                new_admin = User(
                    id=uuid.uuid4(),
                    email='admin@security.local',
                    password_hash=hash_password('Admin@1234'),
                    full_name='Platform Admin',
                    role='admin',
                    is_active=True
                )
                session.add(new_admin)
                await session.commit()
                print("Default admin user initialized (admin@security.local / Admin@1234)")
    except Exception as e:
        print(f"Startup DB warning: {e}")

app.include_router(auth_router)
app.include_router(users_router)

@app.get('/api/v1/health')
@app.get('/api/health')
@app.get('/health')
@app.get('/api')
async def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}
