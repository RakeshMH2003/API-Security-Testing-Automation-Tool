from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import settings

engine = create_async_engine(settings.get_database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

_tables_created = False

async def create_tables():
    global _tables_created
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _tables_created = True

async def get_db():
    global _tables_created
    if not _tables_created:
        try:
            await create_tables()
        except Exception as e:
            print(f"DB auto-init info: {e}")
    async with AsyncSessionLocal() as session:
        yield session
