import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, select, update
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dotenv import load_dotenv
#charhao is gay
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
# read the fucking database url from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL 環境變數未設置。")
    raise ValueError("DATABASE_URL 環境變數未設置")

# the fucking async engine
engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

# ORM Models
class User(Base):
    """
    使用者資料庫模型。
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False) # store the fucking hashed password
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

# Database Operations Class
class Database:#pack all the fucking user async operation
    def __init__(self):
        self.async_session = AsyncSessionLocal

    async def create_user(self, name: str, email: str, password: str) -> User:
        async with self.async_session() as session:
            new_user = User(name=name, email=email, password=password)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            logger.info(f"使用者已建立: {email}")
            return new_user

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.async_session() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.async_session() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def update_user_password(self, user_id: int, hashed_password: str) -> None:
        async with self.async_session() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(password=hashed_password)
            )
            await session.execute(stmt)
            await session.commit()
            logger.info(f"使用者 ID {user_id} 的密碼已更新。")

# init the fucking database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)