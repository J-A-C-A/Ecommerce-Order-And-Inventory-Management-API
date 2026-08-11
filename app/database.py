from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

connection = settings.DATABASE_URL
engine = create_async_engine(connection, echo=True)

AsyncLocalSession = async_sessionmaker(bind=engine,expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    db = AsyncLocalSession()
    try:
        yield db
    finally:
        await db.close()