# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from models import Base
# from config import DATABASE_URL

# # DATABASE_URL ="sqlite:///Mydatabase.db"

# engine = create_engine(DATABASE_URL)
# SessionLocal  = sessionmaker(bind=engine)
# Base.metadata.create_all(bind=engine)



# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from config import DATABASE_URL
from models import Base

# engine = create_async_engine(DATABASE_URL)
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)
AsyncSessionLocal = async_sessionmaker(bind = engine,expire_on_commit=False)

async def init_db():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

async def get_db():

    db = AsyncSessionLocal()

    try:
        yield db
    finally:
        await db.close()