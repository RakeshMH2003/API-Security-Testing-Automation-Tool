from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import create_tables
from app.auth.router import router as auth_router

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
    await create_tables()

app.include_router(auth_router)

@app.get('/api/v1/health')
async def health_check():
    return {'status': 'healthy', 'version': '1.0.0'}

import os
# Mount frontend only if the directory exists to avoid errors on startup during dev
if os.path.exists('../../frontend'):
    app.mount("/", StaticFiles(directory="../../frontend", html=True), name="frontend")
