# pylint:disable=import-error
from typing import AsyncGenerator
from collections.abc import Generator
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.database import (
    SessionLocal,
    async_session_maker,
)


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и закрывает её после обработки.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
