from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string to the Docker Postgres database
# Update localhost:5432 to localhost:5435
DATABASE_URL = "postgresql+asyncpg://admin:flashsale_pass@localhost:5435/flashsale"

engine = create_async_engine(DATABASE_URL, echo=False)

# This is the session factory we will use to talk to the DB
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency for FastAPI to get DB sessions
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session