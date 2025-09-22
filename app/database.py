import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLITE_DATABASE_URL = os.getenv("SQLITE_DATABASE_URL")


DATABASE_URL = os.getenv("DATABASE_URL")

# Синхронное подключение
engine = create_engine(SQLITE_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Асинхронное подключение
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(
    bind=async_engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
