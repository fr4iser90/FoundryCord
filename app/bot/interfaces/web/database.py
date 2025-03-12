from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import Settings

settings = Settings()

# PostgreSQL connection string
if settings.DATABASE_URL.startswith('postgresql://'):
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)
else:
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Define Base class for models
Base = declarative_base()

async def get_db():
    """
    Dependency to get a database session
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close() 