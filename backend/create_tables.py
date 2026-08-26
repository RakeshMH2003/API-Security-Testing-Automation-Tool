import asyncio
import asyncpg
from app.database import engine, Base
from app.config import settings

async def main():
    # Parse DB connection info from settings
    # assuming format: postgresql+asyncpg://user:pass@host:port/dbname
    db_url = settings.DATABASE_URL
    
    # Extract components
    base_url = db_url.split('/apisec')[0]
    default_db_url = base_url + '/postgres'
    
    try:
        # Connect to default database
        conn = await asyncpg.connect(default_db_url.replace('postgresql+asyncpg', 'postgresql'))
        
        # Check if database exists
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'apisec'")
        
        if not exists:
            # Create database
            await conn.execute('CREATE DATABASE apisec')
            print("Database 'apisec' created.")
        else:
            print("Database 'apisec' already exists.")
            
        await conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")

    # Create tables
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

if __name__ == '__main__':
    asyncio.run(main())
